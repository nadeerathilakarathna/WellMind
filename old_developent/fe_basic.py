import cv2
import numpy as np
import tensorflow as tf
import time
from collections import deque
import db_manager  # Assuming db_manager.py contains the database setup and models

# Load trained model
model = tf.keras.models.load_model('models/stress_detection_model_2.h5')

# Load Haar cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Stress detection parameters
WINDOW_SIZE = 5  # 20 minutes / 5s interval = 240 frames
stress_queue = deque(maxlen=WINDOW_SIZE)
STRESS_THRESHOLD = 0.5  # 50% negative emotions


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



session = db_manager.Session()

# Initialize user (for demonstration purposes, replace with actual user retrieval)
user = session.query(db_manager.User).first()  # Assuming you have a user in the database
if user is None:
    db_manager.create_user(
        first_name="John",
        last_name="Doe",
        gender="M",
        birthday="1990-01-01"
    )
    user = session.query(db_manager.User).first()  # Retrieve the newly created user
# Store user ID for later use
user_id = user.user_id 


# Real-time detection loop
last_capture = time.time()
while True:
    ret, frame = cap.read()
    if not ret:
        break
    current_time = time.time()

    # Capture every 5 seconds
    if current_time - last_capture >= 1:# 5 seconds
        face = preprocess_face(frame)
        if face is not None:
            prediction = model.predict(face)[0][0]  # Probability of stress
            stress_queue.append(prediction)
            last_capture = current_time

            # Check stress level over window
            if len(stress_queue) == WINDOW_SIZE:
                stress_percentage = np.mean(stress_queue)
                print(f"Stress Percentage: {stress_percentage:.2f}")

                db_manager.store_facial_expression_data(
                    user_id=user_id,
                    stress_percentage=stress_percentage
                )

                if stress_percentage > STRESS_THRESHOLD:
                    print("Stress Alert: High stress detected!")
                else:
                    print("Stress level: Normal")

    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()