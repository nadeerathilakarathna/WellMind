import sqlite3
from datetime import datetime,timedelta
import pandas as pd
import os
import numpy as np
from recommendation.recommendation_list import recommendations
import random

# DATABASE CONNECTION
DB_NAME = "databases/wellmind.db"

database_path = os.path.dirname(DB_NAME)

try:
    # Check and create folder if not exists
    if not os.path.exists(database_path):
        os.makedirs(database_path)
        print(f"Folder '{database_path}' created.")
    # else:
    #     print(f"Folder '{database_path}' already exists.")
    
    # Try connecting to the database
    # conn = sqlite3.connect(DB_NAME)
    # print("Database connected successfully.")
    # conn.close()

except Exception as e:
    print("An error occurred:", e)

def create_connection():
    return sqlite3.connect(DB_NAME)

# CREATE USER TABLE SQL QUERY
def create_user_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            gender TEXT,
            birthday TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# CREATE NEW USER ACCOUNT
def insert_user(first_name, last_name, gender, birthday):
    conn = create_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO user (first_name, last_name, gender, birthday, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (first_name, last_name, gender, birthday, created_at))
    conn.commit()
    conn.close()

# FETCH LATEST USER
def fetch_latest_user():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, last_name, birthday, gender FROM user ORDER BY user_id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "user_id": result[0],
            "first_name": result[1],
            "last_name": result[2],
            "birthday": result[3],
            "gender": result[4],
        }
    return None


# DELETE USER ACCOUNT
def delete_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Then delete user
    cursor.execute("DELETE FROM user WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

# STORAGE FOR FACIAL EXPRESSION DATA
def store_facial_expression_data(stress_percentage):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facial_expression_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            stress_value REAL NOT NULL
        )
    ''')

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO facial_expression_data (timestamp, stress_value)
        VALUES (?, ?)
    ''', (timestamp, stress_percentage))
    conn.commit()
    conn.close()

# # CAMERA ON AND OFF
# def monitoring_facial_expression(value=None):
#     conn = create_connection()
#     cursor = conn.cursor()

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS facial_expression_monitoring (
#             value BOOLEAN
#         )
#     ''')

#     cursor.execute("SELECT COUNT(*) FROM facial_expression_monitoring")
#     row_count = cursor.fetchone()[0]
#     if row_count == 0:
#         cursor.execute("INSERT INTO facial_expression_monitoring (value) VALUES (?)", (True,))
#         conn.commit()

#     if value is not None:
#         cursor.execute("UPDATE facial_expression_monitoring SET value = ?", (value,))
#         conn.commit()
#         conn.close()
#         return bool(value)
#     else:
#         cursor.execute("SELECT COUNT(*) FROM facial_expression_monitoring")
#         row_count = cursor.fetchone()[0]

        

#         if row_count == 0:
#             cursor.execute("INSERT INTO facial_expression_monitoring (value) VALUES (?)", (True,))
#             conn.commit()
#             conn.close()
#             return True
#         else:
#             cursor.execute("SELECT value FROM facial_expression_monitoring LIMIT 1")
#             result = cursor.fetchone()
#             conn.close()
#             return bool(result[0])



# GET LATEST FACIAL EXPRESSION DATA
def get_latest_facial_expression_data(duration=20, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):

    start_time = datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S")
    before_time = start_time - timedelta(minutes=duration)
    start_time = datetime.strftime(start_time,"%Y-%m-%d %H:%M:%S")
    before_time = datetime.strftime(before_time,"%Y-%m-%d %H:%M:%S")


    conn = create_connection()
    cursor = conn.cursor()


    # cursor.execute("SELECT datetime('now')")
    # print("SQLite now (UTC):", cursor.fetchone()[0])

    # start_time = '2025-07-15 17:04:00'
    # end_time = '2025-07-15 17:05:00'

    cursor.execute("""
        SELECT * FROM facial_expression_data
        WHERE timestamp BETWEEN ? AND ?
    """, (before_time, start_time))

    rows = cursor.fetchall()

    stress_values = [row[2] for row in rows]
    stress_array = np.array(stress_values, dtype=np.float32)

    if len(stress_array) > 0:
        mean_value = np.mean(stress_array)
        # print(len(stress_values))
        mean_value = round(float(mean_value), 2)

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS facial_expression_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            stress_value REAL NOT NULL
        )''')

        conn.commit()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO facial_expression_summary (timestamp, stress_value)
            VALUES (?, ?)
        ''', (timestamp, mean_value))
        conn.commit()
        conn.close()
        return mean_value
    else:
        conn.close()
        return None


# CREATE RECOMMENDATION LOG TABLE
def create_recommendations_log_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            feedback INTEGER,
            updated_at TEXT       
        )
    """)
    conn.commit()
    conn.close()

# SAVE RECOMMENDATION
def insert_recommendation_log(recommendation_id):
    conn = create_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at = created_at  # Initially, updated_at is the same as created_at
    cursor.execute("""
        INSERT INTO recommendations_log (recommendation_id, created_at, feedback, updated_at)
        VALUES (?, ?, ?, ?)
    """, (recommendation_id, created_at, None, updated_at))
    conn.commit()
    conn.close()

# UPDATE RECOMMENDATION WITH USER FEEDBACK
def update_recommendation_feedback(recommendation_id, feedback):
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE recommendations_log
        SET feedback = ?, updated_at = ?
        WHERE recommendation_id = ?
    """, (feedback, updated_at, recommendation_id))
    conn.commit()
    conn.close()


def init_recommendations():
    conn = create_connection()
    cursor = conn.cursor()
    table_name = 'recommendation'

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = cursor.fetchone()

    if result is None:
        # print(f"Table '{table_name}' does NOT exist.")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER NOT NULL,
                content TEXT NOT NULL,
                score INTEGER NOT NULL      
            )
        """)
        conn.commit()

        cursor.executemany("INSERT INTO recommendation (level, content, score) VALUES (?, ?, ?)", [(level, item, 0) for level in recommendations for item in recommendations[level]])
        conn.commit()
    # else:
    #     print(f"Table '{table_name}' exists.")
    conn.commit()
    conn.close()



def get_recommendations(level=1):
    init_recommendations()

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, score FROM recommendation WHERE level = ? AND score = 0", (level,))
    row = cursor.fetchall()
    if len(row) != 0:
        random_row = random.choice(row)
        conn.close()
        # print("database:", random_row)
        return random_row

    else :
        cursor.execute(
        "SELECT id, content, score FROM recommendation WHERE level = ? ORDER BY score DESC LIMIT 10",(level,))
        row = cursor.fetchall()
        random_row = random.choice(row)
        conn.close()
        # print("database:", random_row)
        return random_row


    recommendations = cursor.fetchall()
    conn.close()
    return recommendations


def set_recommendation_score(id, is_liked):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM recommendation WHERE id = ?", (id,))
    current_score = cursor.fetchone()[0]

    if is_liked:
        current_score += 1
    else:
        current_score -= 1

    cursor.execute("UPDATE recommendation SET score = ? WHERE id = ?", (current_score, id))
    conn.commit()
    conn.close()

def get_latest_keystroke_data(duration=25, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    conn = create_connection()
    cursor = conn.cursor()

    start_time = datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S")
    before_time = start_time - timedelta(minutes=duration)
    start_time = datetime.strftime(start_time,"%Y-%m-%d %H:%M:%S")
    before_time = datetime.strftime(before_time,"%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT * FROM keystroke_summary
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (before_time, start_time))


    row = cursor.fetchone()
    if row :
        print(row)
        return row[3] # Latest keystroke stress presentage in keystroke summary
    else:
        print("databse: No keystroke data found")
        return None
    conn.close()


    
def store_realtime_stress(facial_expression_stress,keystroke_stress, stress_level, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS overall_stress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            facial_expression_stress REAL,
            keystroke_stress REAL,
            stress_level INTEGER NOT NULL
        )
    """)
    conn.commit()

    cursor.execute("""
        INSERT INTO overall_stress (timestamp, facial_expression_stress, keystroke_stress, stress_level)
        VALUES (?, ?, ?, ?)
    """, (timestamp, facial_expression_stress, keystroke_stress, stress_level))
    conn.commit()
    conn.close()



def log_error(error_message, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            error_message TEXT NOT NULL
        )
    """)
    conn.commit()

    cursor.execute("""
        INSERT INTO error_log (timestamp, error_message)
        VALUES (?, ?)
    """, (timestamp, error_message))
    conn.commit()
    conn.close()



def get_avatar_status():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avatar_status (
            value BOOLEAN
        )
    """)
    conn.commit()

    cursor.execute("""
        SELECT value FROM avatar_status
    """)
    row = cursor.fetchone()
    conn.close()
    if row:
        return bool(row[0])
    else:
        return True

class Configuration:
    def __init__(self):
        self.configurations = ["avatar_status", "facial_expression_monitoring", "keystroke_dynamics_monitoring", "notification_status"]
        self.table_name = 'configurations'

        def insert_configurations(configurations):
            for self.config in configurations:
                self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name} WHERE configuration = ?", (self.config,))
                if self.cursor.fetchone()[0]==0:
                    self.cursor.execute(f"INSERT INTO {self.table_name} (configuration, value) VALUES (?,?)", (self.config, 1))
                    self.conn.commit()
            self.conn.close()

        

        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';")
        self.result = self.cursor.fetchone()
        if self.result:
            insert_configurations(self.configurations)    

        else:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    configuration TEXT PRIMARY KEY,
                    value INTEGER
                )
                """
            )
            self.conn.commit()

            insert_configurations(self.configurations)
            self.conn.close()

    
    def avatar_is_running(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"SELECT value FROM {self.table_name} WHERE configuration = 'avatar_status'")
        row = self.cursor.fetchone()
        self.conn.close()
        if row:
            return bool(row[0])
        else:
            return True
    
    def avatar_set_status(self, status):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"UPDATE {self.table_name} SET value = ? WHERE configuration = 'avatar_status'", (status,))
        self.conn.commit()
        self.conn.close()

    def facial_expression_is_running(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"SELECT value FROM {self.table_name} WHERE configuration = 'facial_expression_monitoring'")
        row = self.cursor.fetchone()
        self.conn.close()
        if row:
            return bool(row[0])
        else:
            return True
    
    def facial_expression_set_status(self, status):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"UPDATE {self.table_name} SET value = ? WHERE configuration = 'facial_expression_monitoring'", (status,))
        self.conn.commit()
        self.conn.close()

    def keystroke_dynamics_is_running(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"SELECT value FROM {self.table_name} WHERE configuration = 'keystroke_dynamics_monitoring'")
        row = self.cursor.fetchone()
        self.conn.close()
        if row:
            return bool(row[0])
        else:
            return True
    
    def keystroke_dynamics_set_status(self, status):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"UPDATE {self.table_name} SET value = ? WHERE configuration = 'keystroke_dynamics_monitoring'", (status,))
        self.conn.commit()
        self.conn.close()


    def notifications_is_running(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"SELECT value FROM {self.table_name} WHERE configuration = 'notification_status'")
        row = self.cursor.fetchone()
        self.conn.close()
        if row:
            return bool(row[0])
        else:
            return True
    
    def notifications_set_status(self, status):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"UPDATE {self.table_name} SET value = ? WHERE configuration = 'notification_status'", (status,))
        self.conn.commit()
        self.conn.close()

# Dashboard visualizations
def get_stress_metrics():
    conn = create_connection()
    cursor = conn.cursor()

    # 1. Get the latest stress record
    cursor.execute("""
        SELECT facial_expression_stress, keystroke_stress 
        FROM overall_stress 
        ORDER BY id DESC LIMIT 1
    """)
    result = cursor.fetchone()

    facial_stress = keystroke_stress = current_stress = None
    if result:
        facial_stress = float(result[0])
        keystroke_stress = float(result[1])
        current_stress = round((facial_stress + keystroke_stress) / 2, 2)

    # 2. Get today's date string
    today_str = datetime.now().date().isoformat()

    # 3. Fetch today's records
    cursor.execute("""
        SELECT facial_expression_stress, keystroke_stress 
        FROM overall_stress
        WHERE DATE(timestamp) = DATE(?)
    """, (today_str,))

    rows = cursor.fetchall()
    conn.close()

    # 4. Calculate average and peak stress
    avg_stress = None
    peak_stress = None

    if rows:
        total_stress = 0
        max_stress = 0

        for row in rows:
            try:
                facial = float(row[0])
                keystroke = float(row[1])
                stress_level = (facial + keystroke) / 2
                total_stress += stress_level

                if stress_level > max_stress:
                    max_stress = stress_level
            except (TypeError, ValueError):
                continue

        count = len(rows)
        if count > 0:
            avg_stress = round(total_stress / count, 2)
            peak_stress = round(max_stress, 2)

    # 5. Return dictionary with all metrics
    return {
        "Current Stress": f"{current_stress:.2f}%" if current_stress is not None else "No data",
        "Average Stress": f"{avg_stress:.2f}%" if avg_stress is not None else "No data",
        "Peak Stress": f"{peak_stress:.2f}%" if peak_stress is not None else "No data"
    }

def get_feedback_counts():
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN feedback = 1 THEN 1 ELSE 0 END) AS likes,
                SUM(CASE WHEN feedback = 0 THEN 1 ELSE 0 END) AS unlikes
            FROM recommendations_log
            WHERE feedback IS NOT NULL
        """)
        result = cursor.fetchone()
        likes, unlikes = result if result else (0, 0)
        return {"likes": likes or 0, "unlikes": unlikes or 0}
    except Exception as e:
        print("Error fetching feedback counts:", e)
        return {"likes": 0, "unlikes": 0}
    finally:
        conn.close()


def fetch_recent_recommendations(limit=5):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                rl.id, 
                rl.recommendation_id, 
                rl.created_at, 
                rl.feedback,
                r.content
            FROM recommendations_log rl
            JOIN recommendation r ON rl.recommendation_id = r.id
            ORDER BY datetime(rl.created_at) DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()

        recommendations = []
        for row in rows:
            log_id, rec_id, created_at, feedback, content = row

            # Convert feedback: 1 = liked, 0 = unliked
            if feedback == 1:
                reaction = "liked"
            elif feedback == 0:
                reaction = "unliked"
            else:
                reaction = "unknown"  # This should not happen due to IS NOT NULL

            recommendations.append({
                "id": log_id,
                "recommendation": content,
                "timestamp": created_at,
                "reaction": reaction
            })

        return recommendations

    except Exception as e:
        print("Error fetching recommendations:", e)
        return []

    finally:
        conn.close()

def fetch_user_dashboard(option='daily',date=None):
    conn = create_connection()
    cursor = conn.cursor()


    if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
            # date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=-1)
            # date = date.strftime("%Y-%m-%d")

    if option == 'daily':
        point_date = date + ' 23:59:59'
        before_date = date + ' 00:00:00'
    if option == 'weekly':
        point_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d") + ' 23:59:59'
        before_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=-7)
        before_date = before_date.strftime("%Y-%m-%d") + ' 00:00:00'
    if option == 'monthly':
        point_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d") + ' 23:59:59'
        before_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=-30)
        before_date = before_date.strftime("%Y-%m-%d") + ' 00:00:00'
    if option == 'yearly':
        point_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d") + ' 23:59:59'
        before_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=-365)
        before_date = before_date.strftime("%Y-%m-%d") + ' 00:00:00'
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS overall_stress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            facial_expression_stress REAL,
            keystroke_stress REAL,
            stress_level INTEGER NOT NULL
        )
    """)
    conn.commit()

    cursor.execute("""
    SELECT *,
           CASE
               WHEN facial_expression_stress = 0 OR keystroke_stress = 0 THEN
                   facial_expression_stress + keystroke_stress
               ELSE
                   (facial_expression_stress + keystroke_stress) / 2
            END AS overall
        FROM overall_stress
        WHERE timestamp BETWEEN ? AND ?
    """, (before_date, point_date))

    # print(f'point date: {point_date}')
    # print(f'before date: {before_date}')

    rows = cursor.fetchall()

    data = {
        'info': {
            'option': option,
            'point_date': point_date,
            'before_date': before_date,
        },
        'rows': rows
    }

    conn.close()
    return data
