from services.database import get_latest_facial_expression_data
from datetime import datetime
import time

def calculate_facial_expression_summary():
    duration = 5
    print('''
    
    
    FE SUMMARY
  
    
    ''')
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        value = get_latest_facial_expression_data(duration, timestamp)
        print(f"Timestamp: {timestamp} - Stress Value: {value}")
        time.sleep(60*5)

