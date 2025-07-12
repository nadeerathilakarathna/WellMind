import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 = all logs, 1 = filter INFO, 2 = +WARNING, 3 = +ERROR


import cv2
import numpy as np
import tensorflow as tf
import time
from collections import deque
# import db_manager  # You must have this file with your DB models
import multiprocessing
from multiprocessing import Process, Manager
from tensorflow.keras.models import load_model



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

# Now load the model
print(" Loading model...")
#model = load_model('models/sequential_model.h5')
model = load_model('models/sequential_model_improved.h5')
# model = load_model('models/sequential_model_improved.h5', compile=False)

#model = load_model('models/cbam_cnn_stress_detection.h5', custom_objects={'CBAM': CBAM})
#model = load_model('models/cbam_cnn_stress_detection_improved.h5', custom_objects={'CBAM': CBAM})



# # Load trained model
# model = tf.keras.models.load_model('models/cbam_cnn_stress_detection.h5')

# Load Haar cascade
#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

print(" Opening webcam...")
# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print(" Starting detection loop...")
# Stress detection parameters
WINDOW_SIZE = 5
stress_queue = deque(maxlen=WINDOW_SIZE)
STRESS_THRESHOLD = 0.5

def preprocess_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    (x, y, w, h) = faces[0]
    face = gray[y:y + h, x:x + w]
    face = cv2.resize(face, (48, 48))
    face = face.astype('float32') / 255.0
    face = np.expand_dims(face, axis=(0, -1))
    return face

if __name__ == "__main__":
    multiprocessing.freeze_support()
    with Manager() as manager:
        stress_list = manager.list()

        ### Start plotter process
        # plot_process = Process(target=stress_plotter.live_plot, args=(stress_list,))
        # plot_process.start()

        ### Initialize DB session and get user ID as user_id variable

        # Real-time detection loop
        last_capture = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            current_time = time.time()

            if current_time - last_capture >= 1:  # Every 1s
                face = preprocess_face(frame)
                if face is not None:
                    prediction = model.predict(face)[0][0]
                    stress_queue.append(prediction)
                    stress_list.append(prediction)
                    last_capture = current_time

                    if len(stress_queue) == WINDOW_SIZE:
                        stress_percentage = np.mean(stress_queue)
                        print(f"Stress Percentage: {stress_percentage:.2f}")

                        ### Store stress data in the database using user_id variable and current stress_presentage

                        if stress_percentage > STRESS_THRESHOLD:
                            print("Stress Alert: High stress detected!")
                        else:
                            print("Stress level: Normal")

            # cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        # plot_process.terminate()
