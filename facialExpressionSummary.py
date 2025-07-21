from services.database import get_latest_facial_expression_data,get_latest_keystroke_data
from datetime import datetime
import time
from recommendations import start_recommendation

def calculate_facial_expression_summary():
    duration = 1 # in minutes
    print('PRINTING FE SUMMARY')
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        facial_value = get_latest_facial_expression_data(duration, timestamp)
        keystroke_value = get_latest_keystroke_data(duration,timestamp=timestamp)

        print(f"Timestamp: {timestamp} - Overall Facial Stress Value: {facial_value}")
        print(f"Timestamp: {timestamp} - Overall Keystroke Stress Value: {keystroke_value}")

        start_recommendation(facial_value, keystroke_value)
        
        time.sleep(60*duration)

