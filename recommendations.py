from engine.recommender import get_recommendation
from engine.tracker import save_recommendation, update_feedback
from utils.notification import show_modern_notification
import time

def parse_and_average_input(prompt: str, validation_type: str) -> float:
    raw = input(prompt).strip()
    try:
        values = [float(v.strip()) for v in raw.split(',') if v.strip()]

        if not values:
            raise ValueError("Input must include at least one valid number.")

        for val in values:
            if val < 0 or val > 100:
                raise ValueError(f"Value {val} is out of range (0–100).")
            if validation_type == "facial":
                if val < 50:
                    raise ValueError(f"Facial analysis value {val} must be 50 or higher.")
            elif validation_type == "keystroke":
                if val % 10 != 0:
                    raise ValueError(f"Keystroke analysis value {val} must be a multiple of 10.")

        average = sum(values) / len(values)
        return round(average, 2)  # Keep two decimal places
    except Exception as e:
        raise ValueError(f"Invalid input: {e}")


def show_notification():
    try:
        facial = parse_and_average_input("Enter facial analysis value(s) (50–100): ", "facial")
        keystroke = parse_and_average_input("Enter keystroke analysis value(s) (multiples of 10, 0–100): ", "keystroke")

        rec_id, recommendation,score = get_recommendation(facial, keystroke)

        if rec_id is None:
            print(f"\n❌ {recommendation}")
            return

        save_recommendation(rec_id)

        def on_like():
            update_feedback(rec_id, 1)
            print("✅ You liked the recommendation.")

        def on_dislike():
            update_feedback(rec_id, 0)
            print("❌ You disliked the recommendation.")

        show_modern_notification(rec_id, recommendation, on_like, on_dislike)

        print("🔔 Recommendation shown as notification.")
        time.sleep(20)  # wait so GUI stays visible

    except ValueError as e:
        print(f"\n⚠️ Error: {e}")

# Call the function to
show_notification();