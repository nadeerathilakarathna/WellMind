import cv2
import numpy as np
import tensorflow as tf
import time
from collections import deque
import db_manager  # You must have this file with your DB models
from multiprocessing import Process, Manager
import stress_plotter
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

model1 = load_model('models/sequential_model.h5')
model2 = load_model('models/sequential_model_improved.h5')
model3 = load_model('models/cbam_cnn_stress_detection.h5', custom_objects={'CBAM': CBAM})
model4 = load_model('models/cbam_cnn_stress_detection_improved.h5', custom_objects={'CBAM': CBAM})



# # Load trained model
# model = tf.keras.models.load_model('models/cbam_cnn_stress_detection.h5')

# Load Haar cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Stress detection parameters
WINDOW_SIZE = 5
stress_queue1 = deque(maxlen=WINDOW_SIZE)
stress_queue2 = deque(maxlen=WINDOW_SIZE)
stress_queue3 = deque(maxlen=WINDOW_SIZE)
stress_queue4 = deque(maxlen=WINDOW_SIZE)
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
    with Manager() as manager:
        stress_list1 = manager.list()
        stress_list2 = manager.list()
        stress_list3 = manager.list()
        stress_list4 = manager.list()

        # Start plotter process
        plot_process = Process(target=stress_plotter.live_plot_multiple_models, args=(stress_list1,stress_list2, stress_list3, stress_list4))
        plot_process.start()

        # DB session
        session = db_manager.Session()
        user = session.query(db_manager.User).first()
        if user is None:
            db_manager.create_user(
                first_name="John",
                last_name="Doe",
                gender="M",
                birthday="1990-01-01"
            )
            user = session.query(db_manager.User).first()
        user_id = user.user_id

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
                    prediction1 = model1.predict(face)[0][0]
                    prediction2 = model2.predict(face)[0][0]
                    prediction3 = model3.predict(face)[0][0]    
                    prediction4 = model4.predict(face)[0][0]

                    stress_queue1.append(prediction1)
                    stress_queue2.append(prediction2)
                    stress_queue3.append(prediction3)
                    stress_queue4.append(prediction4)

                    stress_list1.append(prediction1)
                    stress_list2.append(prediction2)
                    stress_list3.append(prediction3)
                    stress_list4.append(prediction4)

                    last_capture = current_time

                    if len(stress_queue1) == WINDOW_SIZE:
                        stress_percentage1 = np.mean(stress_queue1)
                        print(f"Stress Percentage: {stress_percentage1:.2f}, Model 1")

                        db_manager.store_facial_expression_data(
                            user_id=user_id,
                            stress_percentage=stress_percentage1
                        )

                    if len(stress_queue2) == WINDOW_SIZE:
                        stress_percentage2 = np.mean(stress_queue2)
                        print(f"Stress Percentage: {stress_percentage2:.2f} Model 2")

                       
                    if len(stress_queue3) == WINDOW_SIZE:
                        stress_percentage3 = np.mean(stress_queue3)
                        print(f"Stress Percentage: {stress_percentage3:.2f} Model 3")

                    if len(stress_queue4) == WINDOW_SIZE:
                        stress_percentage4 = np.mean(stress_queue4)
                        print(f"Stress Percentage: {stress_percentage4:.2f} Model 4")

                    
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        plot_process.terminate()
