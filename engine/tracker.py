from services.database import (
    create_connection,
    create_recommendations_log_table,
    insert_recommendation_log,
    update_recommendation_feedback,
    set_recommendation_score
)

# ✅ Ensure the table is created at the beginning
create_recommendations_log_table()


def has_been_shown(rec_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM recommendations_log WHERE recommendation_id = ?
        """, (rec_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"[ERROR] has_been_shown: {e}")
        return False


def was_disliked(rec_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT feedback FROM recommendations_log WHERE recommendation_id = ?
        """, (rec_id,))
        row = cursor.fetchone()
        conn.close()
        return row is not None and row[0] == 0
    except Exception as e:
        print(f"[ERROR] was_disliked: {e}")
        return False


def save_recommendation(rec_id):
    try:
        insert_recommendation_log(rec_id)
    except Exception as e:
        print(f"[ERROR] save_recommendation: {e}")


def update_feedback(rec_id, feedback):
    try:
        update_recommendation_feedback(rec_id, feedback)
        set_recommendation_score(rec_id, bool(feedback))

    except Exception as e:
        print(f"[ERROR] update_feedback: {e}")
