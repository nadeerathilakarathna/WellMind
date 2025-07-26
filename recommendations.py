from engine.recommender import get_recommendation
from engine.tracker import save_recommendation, update_feedback
from utils.notification import show_modern_notification
import time
from services.database import Configuration

def start_recommendation(facial_stress=None, keystroke_stress=None):
    rec_id, recommendation,score,level = get_recommendation(facial_stress, keystroke_stress)

    if not (rec_id is None):

        save_recommendation(rec_id)

        def on_like():
            update_feedback(rec_id, 1)
            print("✅ You liked the recommendation.")

        def on_dislike():
            update_feedback(rec_id, 0)
            print("❌ You disliked the recommendation.")
        
        configuration = Configuration()
        if configuration.notifications_is_running():
            show_modern_notification(rec_id, recommendation, on_like, on_dislike)

        print("🔔 Recommendation shown as notification.")
        time.sleep(20)  # wait so GUI stays visible

    else:
        print(f"\n❌ No Need to recommendation")



if __name__ == "__main__":
    facial = float(input("Enter facial analysis value(s) (0–100): "))
    keystroke = float(input("Enter keystroke analysis value(s) (0–100): "))
    start_recommendation(facial,keystroke)