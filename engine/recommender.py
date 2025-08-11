import os
import random
from engine.tracker import has_been_shown, was_disliked
from services.database import get_recommendations as get_recommendation_from_db
from services.database import store_realtime_stress
import services.database as db
from datetime import datetime

def get_level(score):
    if score is None:
        return 0
    elif 0 <= score <= 50:
        return 0
    elif 50 <= score <= 60:
        return 1
    elif 60 <= score <= 70:
        return 2
    elif 70 <= score <= 80:
        return 3
    elif 80 <= score <= 90:
        return 4
    elif 90 <= score <= 100:
        return 5
    else:
        print(f"Type: {type(score)}, Value: {score}")
        db.log_error(f"Invalid score: {score} in get_level() Type: {type(score)}")
        raise ValueError("Score must be between 0 and 100.")


def get_recommendation(facial_value, keystroke_value) -> tuple:
    master_facial_value = facial_value
    master_keystroke_value = keystroke_value

    if facial_value is None:
        facial_value = 0
    if keystroke_value is None:
        keystroke_value = 0
    
    if facial_value == 0 or keystroke_value == 0:
        final_level = get_level(max(facial_value, keystroke_value))
    else:
        final_level = get_level((facial_value + keystroke_value)/2)
        
    # level_facial = get_level(facial_value) #Stress level > None = 0 and 1,2,3,4,5
    # level_keystroke = get_level(keystroke_value) #Stress level > None = 0 and 1,2,3,4,5
    # final_level = level_facial if level_facial == level_keystroke else max(level_facial, level_keystroke)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    store_realtime_stress(master_facial_value, master_keystroke_value, final_level,timestamp)

    if final_level == 0:
        return (None,None,None,0) #No recommendations

    return get_recommendation_from_db(final_level) + (final_level,) # recommendation tuple = (rec_id, recommendation, score, level)