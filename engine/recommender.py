import os
import random
from engine.tracker import has_been_shown, was_disliked

RECOMMENDATION_DIR = "data/recommendations"


def get_level(score: int) -> int:
    if 0 <= score <= 20:
        return 1
    elif 21 <= score <= 40:
        return 2
    elif 41 <= score <= 60:
        return 3
    elif 61 <= score <= 80:
        return 4
    elif 81 <= score <= 100:
        return 5
    else:
        raise ValueError("Score must be between 0 and 100.")


def load_recommendations_for_level(level: int) -> list:
    file_path = os.path.join(RECOMMENDATION_DIR, f"level_{level}.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Recommendation file for level {level} not found.")

    with open(file_path, "r", encoding="utf-8") as file:
        raw = [line.strip() for line in file if line.strip()]

    # Format: RL01001: Take a deep breath
    recommendations = []
    for line in raw:
        if ':' in line:
            rec_id, text = line.split(':', 1)
            rec_id = rec_id.strip()
            text = text.strip()
            if not has_been_shown(rec_id) and not was_disliked(rec_id):
                recommendations.append((rec_id, text))
    return recommendations


def get_recommendation(facial_value: int, keystroke_value: int) -> tuple:
    level_facial = get_level(facial_value)
    level_keystroke = get_level(keystroke_value)
    final_level = level_facial if level_facial == level_keystroke else max(level_facial, level_keystroke)

    recommendations = load_recommendations_for_level(final_level)
    if not recommendations:
        return None, "No new recommendations available."

    return random.choice(recommendations)
