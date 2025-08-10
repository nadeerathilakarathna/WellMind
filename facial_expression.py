import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 = all logs, 1 = filter INFO, 2 = +WARNING, 3 = +ERROR

from services.database import log_error

import cv2
import numpy as np
import tensorflow as tf
import time
from collections import deque
# import db_manager  # You must have this file with your DB models
import multiprocessing
from multiprocessing import Process, Manager
from tensorflow.keras.models import load_model
from datetime import datetime

from services.database import store_facial_expression_data, Configuration


def facial_expression_monitoring():
    
    # Make sure this class is available before loading
    class CBAM(tf.keras.layers.Layer):
        def __init__(self, reduction_ratio=8, **kwargs):  # <-- ADD **kwargs
            super(CBAM, self).__init__(**kwargs)          # <-- PASS **kwargs
            self.reduction_ratio = reduction_ratio

        def build(self, input_shape):
            channels = input_shape[-1]
            self.channel_attention = tf.keras.Sequential([
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dense(channels // self.reduction_ratio, activation='relu'),
                tf.keras.layers.Dense(channels, activation='sigmoid')
            ])
            self.spatial_attention = tf.keras.layers.Conv2D(1, (7, 7), padding='same', activation='sigmoid')

        def call(self, inputs):
            avg_pool = tf.reduce_mean(inputs, axis=[1, 2], keepdims=True)
            channel_att = self.channel_attention(avg_pool)
            channel_refined = tf.keras.layers.Multiply()([inputs, channel_att])
            spatial_att = self.spatial_attention(channel_refined)
            return tf.keras.layers.Multiply()([channel_refined, spatial_att])

    def is_camera_available(index=0):
        """Check if camera is available without keeping it open"""
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            return ret
        cap.release()
        return False

    def wait_for_camera(index=0, retry_interval=5):
        """Wait until camera becomes available"""
        print("Checking camera availability...")
        while not is_camera_available(index):
            print(f"Camera not available, retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
        
        # Now actually open the camera
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print("Camera connected successfully.")
            return cap
        else:
            print("Failed to open camera after detection. Retrying...")
            return wait_for_camera(index, retry_interval)

    def setup_camera(cap):
        """Configure camera settings"""
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return cap

    # Wait for camera to be available before proceeding
    print("Waiting for camera to become available...")
    if not is_camera_available(0):
        print("No camera detected. Waiting for camera connection...")
        cap = wait_for_camera(0)
    else:
        print("Camera detected. Initializing...")
        cap = cv2.VideoCapture(0)
    
    cap = setup_camera(cap)
        
    # Now load the model (only after camera is confirmed)
    print("Loading model...")

    model = load_model('models/facial/facial_expression_model.h5')

    # Load Haar cascade
    #face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

    configuration = Configuration()

    if datetime.now() < datetime(2025, 8, 15):
        configuration.facial_expression_set_status(True)

    print("Starting detection loop...")
    # Stress detection parameters
    WINDOW_SIZE = 1
    stress_queue = deque(maxlen=WINDOW_SIZE)
    STRESS_THRESHOLD = 0.5

    def preprocess_face(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        if len(faces) == 0:
            return None
        (x, y, w, h) = faces[0]
        face = gray[y:y + h, x:x + w]
        face = cv2.resize(face, (48, 48))
        face = face.astype('float32') / 255.0
        face = np.expand_dims(face, axis=(0, -1))
        return face

    with Manager() as manager:
        stress_list = manager.list()

        ### Start plotter process
        # plot_process = Process(target=stress_plotter.live_plot, args=(stress_list,))
        # plot_process.start()

        ### Initialize DB session and get user ID as user_id variable

        # Real-time detection loop
        last_capture = time.time()
        
        camera_error_count = 0
        max_camera_errors = 3
        
        while True:
            if configuration.facial_expression_is_running() == False:
                if cap.isOpened():
                    cap.release()
                print("Facial expression monitoring paused...")
                time.sleep(2)  # Wait before checking again
                continue
            else:
                # Check if camera is still available and reopen if needed
                if not cap.isOpened():
                    print("Camera disconnected. Attempting to reconnect...")
                    if is_camera_available(0):
                        cap = cv2.VideoCapture(0)
                        cap = setup_camera(cap)
                        camera_error_count = 0
                        print("Camera reconnected successfully.")
                    else:
                        camera_error_count += 1
                        if camera_error_count >= max_camera_errors:
                            print("Camera unavailable after multiple attempts. Waiting for camera...")
                            cap = wait_for_camera(0)
                            cap = setup_camera(cap)
                            camera_error_count = 0
                        else:
                            print(f"Camera not available (attempt {camera_error_count}/{max_camera_errors}). Retrying...")
                            time.sleep(2)
                            continue

            ret, frame = cap.read()
            if not ret:
                print("Failed to read from camera. Checking camera status...")
                camera_error_count += 1
                if camera_error_count >= max_camera_errors:
                    print("Multiple camera read failures. Reconnecting...")
                    cap.release()
                    cap = wait_for_camera(0)
                    cap = setup_camera(cap)
                    camera_error_count = 0
                time.sleep(1)
                continue
            
            # Reset error count on successful frame read
            camera_error_count = 0
            current_time = time.time()

            if current_time - last_capture >= 1:  # Every 1s
                face = preprocess_face(frame)
                if face is not None:
                    try:
                        prediction = model.predict(face, verbose=0)[0][0]
                        stress_queue.append(prediction)
                        stress_list.append(prediction)
                        last_capture = current_time

                        if len(stress_queue) == WINDOW_SIZE:
                            stress_percentage = np.mean(stress_queue)
                            print(f"Stress Percentage: {stress_percentage:.2f}")

                            store_facial_expression_data(round(float(stress_percentage)*100, 2))

                            ### Store stress data in the database using user_id variable and current stress_presentage

                            if stress_percentage > STRESS_THRESHOLD:
                                print("Stress Alert: High stress detected!")
                            else:
                                print("Stress level: Normal")
                    except Exception as e:
                        print(f"Error during prediction: {e}")
                        log_error(str(e))

            #cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
        # plot_process.terminate()