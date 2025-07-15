import time
import threading
from pynput import keyboard
import numpy as np
import joblib
import sqlite3
from datetime import datetime
import pandas as pd


model = joblib.load('models/keystroke/random_forest_stress_model.joblib')

key_down_times = {}
hold_times = []
flight_times = []
last_key_up_time = None
error_count = 0
key_events_count = 0

lock = threading.Lock()

def on_press(key):
    global key_down_times, key_events_count
    try:
        k = key.char
    except AttributeError:
        k = str(key)

    with lock:
        key_down_times[k] = time.time()
        key_events_count += 1

def on_release(key):
    global hold_times, flight_times, last_key_up_time, error_count
    try:
        k = key.char
    except AttributeError:
        k = str(key)

    now = time.time()

    with lock:
        if k in key_down_times:
            hold_time = (now - key_down_times[k]) * 1000
            hold_times.append(hold_time)
            del key_down_times[k]

            if last_key_up_time is not None:
                flight_time = (now - last_key_up_time) * 1000
                flight_times.append(flight_time)
            last_key_up_time = now
        else:
            error_count += 1


    if key == keyboard.Key.pause:
        return False


def calculate_features(duration_minutes=2):
    global error_count, key_events_count

    with lock:
        ht = hold_times.copy()
        ft = flight_times.copy()
        ec = error_count
        kc = key_events_count
        hold_times.clear()
        flight_times.clear()

    mean_hold = np.mean(ht) if ht else 0
    mean_flight = np.mean(ft) if ft else 0
    typing_speed = (kc / (duration_minutes * 60)) * 60
    error_rate = (ec / kc) * 100 if kc > 0 else 0

    with lock:
        error_count = 0
        key_events_count = 0

    return [mean_hold, mean_flight, typing_speed, error_rate]

def predict_and_store():
    conn_thread = sqlite3.connect('databases/wellmind.db', check_same_thread=False)
    cursor_thread = conn_thread.cursor()
    cursor_thread.execute('''
        CREATE TABLE IF NOT EXISTS keystroke_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            stress_label INTEGER NOT NULL,
            stress_percentage REAL NOT NULL
        )
    ''')
    conn_thread.commit()

    feature_names = ['mean_hold_time', 'mean_flight_time', 'avg_typing_speed', 'avg_error_rate']
    MIN_KEYSTROKES = 8
    interval_minutes = 0.1 #2
    summary_window = 0.5  # in minutes #20
    max_intervals = summary_window // interval_minutes

    predictions = []
    while True:
        time.sleep(interval_minutes * 60)

        features = calculate_features(duration_minutes=interval_minutes)
        total_keys = int((features[2] * (interval_minutes * 60)) / 60)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if total_keys < MIN_KEYSTROKES:
            print(f"[{timestamp}] Skipped: not enough keystrokes ({total_keys} pressed)")
            predictions.append(None)

        else:

            features_df = pd.DataFrame([features], columns=feature_names)

            pred_label = model.predict(features_df)[0]

            pred_prob = model.predict_proba(features_df)[0][1]

            predictions.append(pred_label)

            print(f"[{timestamp}] 2-min Prediction: {pred_label} (stress prob: {pred_prob:.2f})")

         # If 20 minutes (10 intervals) passed

        if len(predictions) == max_intervals:

            stress_count = sum(1 for p in predictions if p == 1)

            stress_percentage = (stress_count / max_intervals) * 100
            majority_label = 1 if stress_percentage >= 50 else 0

            summary_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{summary_timestamp}] 🔍 20-min Summary → Stress %: {stress_percentage:.1f}%, Label: {majority_label}")

            cursor_thread.execute(
                'INSERT INTO keystroke_summary (timestamp, stress_label, stress_percentage) VALUES (?, ?, ?)',
                (summary_timestamp, majority_label, stress_percentage)
            )
            conn_thread.commit()

            predictions.clear()  # reset for next 20-min block




'''
def main():
    print("Starting keystroke capture. Press ESC to stop.")

    pred_thread = threading.Thread(target=predict_and_store, daemon=True)
    pred_thread.start()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    print("Program ended.")

if __name__ == "__main__":
    main()
'''