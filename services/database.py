import sqlite3
from datetime import datetime,timedelta
import pandas as pd
import os
import numpy as np
from recommendation.recommendation_list import recommendations
import random

# DATABASE CONNECTION
DB_NAME = "databases/wellmind.db"

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

    # Optional: delete user preferences first for referential integrity
    cursor.execute("DELETE FROM user_preferences_mapping WHERE user_id = ?", (user_id,))

    # Then delete user
    cursor.execute("DELETE FROM user WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

# CREATE PREFERENCES CATEGORY AND PREFERENCES TABLE
# def create_preferences_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences_category (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
            preference_name TEXT,
            category_id INTEGER,
            created_at TEXT,
            FOREIGN KEY (category_id) REFERENCES preferences_category (category_id)
        )
    """)
    conn.commit()
    conn.close()

# IMPORT DATA TO THE PREFERENCES TABLE
# def import_preferences_from_excel(excel_path="assets/documents/preferences.xlsx"):
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        return

    df = pd.read_excel(excel_path)

    conn = create_connection()
    cursor = conn.cursor()

    # --- Delete existing data ---
    cursor.execute("DELETE FROM preferences")
    cursor.execute("DELETE FROM preferences_category")
    conn.commit()

    # --- Prepare for inserting new data ---
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    category_map = {}

    for _, row in df.iterrows():
        preference_name = row['Preference Name']
        category_name = row['Category']

        # Insert category if not already inserted
        if category_name not in category_map:
            cursor.execute("SELECT category_id FROM preferences_category WHERE category_name = ?", (category_name,))
            category = cursor.fetchone()
            if category:
                category_id = category[0]
            else:
                cursor.execute(
                    "INSERT INTO preferences_category (category_name, created_at) VALUES (?, ?)",
                    (category_name, created_at)
                )
                category_id = cursor.lastrowid
            category_map[category_name] = category_id
        else:
            category_id = category_map[category_name]

        # Insert preference
        cursor.execute("""
            INSERT INTO preferences (preference_name, category_id, created_at)
            VALUES (?, ?, ?)
        """, (preference_name, category_id, created_at))

    conn.commit()
    conn.close()

# CREATE USER PREFERENCES MAPPING TABLE
# def create_user_preferences_mapping_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            preference_id INTEGER,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES user(user_id),
            FOREIGN KEY (preference_id) REFERENCES preferences(preference_id)
        )
    """)
    conn.commit()
    conn.close()

# FETCH PREFERENCE CATEGORIES SQL QUERY
# def get_all_categories():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, category_name FROM preferences_category ORDER BY category_name")
    categories = cursor.fetchall()
    conn.close()
    return categories

# FETCH CATEGORY WISE PREFERENCES SQL QUERY
# def get_preferences_by_category(category_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT preference_id, preference_name FROM preferences 
        WHERE category_id = ? ORDER BY preference_name
    """, (category_id,))
    preferences = cursor.fetchall()
    conn.close()
    return preferences

# FETCH PREFERENCES WITH ID
# def get_preference_id_by_name(name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT preference_id FROM preferences WHERE preference_name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# SAVE USER SELECTED PREFERENCES ON THE DATABASE
# def insert_user_preference_mapping(user_id, preference_id):
    conn = create_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO user_preferences_mapping (user_id, preference_id, created_at)
        VALUES (?, ?, ?)
    """, (user_id, preference_id, created_at))
    conn.commit()
    conn.close()

# FETCH USER PREFERENCES LIST
# def get_user_preferences_by_user_id(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pc.category_name, p.preference_name
        FROM user_preferences_mapping upm
        JOIN preferences p ON upm.preference_id = p.preference_id
        JOIN preferences_category pc ON p.category_id = pc.category_id
        WHERE upm.user_id = ?
        ORDER BY pc.category_name, p.preference_name
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    result = {}
    for category_name, preference_name in rows:
        if category_name not in result:
            result[category_name] = []
        result[category_name].append(preference_name)
    return result

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

# CAMERA ON AND OFF
def monitoring_facial_expression(value=None):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facial_expression_monitoring (
            value BOOLEAN
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM facial_expression_monitoring")
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        cursor.execute("INSERT INTO facial_expression_monitoring (value) VALUES (?)", (True,))
        conn.commit()

    if value is not None:
        cursor.execute("UPDATE facial_expression_monitoring SET value = ?", (value,))
        conn.commit()
        conn.close()
        return bool(value)
    else:
        cursor.execute("SELECT COUNT(*) FROM facial_expression_monitoring")
        row_count = cursor.fetchone()[0]

        

        if row_count == 0:
            cursor.execute("INSERT INTO facial_expression_monitoring (value) VALUES (?)", (True,))
            conn.commit()
            conn.close()
            return True
        else:
            cursor.execute("SELECT value FROM facial_expression_monitoring LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            return bool(result[0])

# GET LATEST FACIAL EXPRESSION DATA
def get_latest_facial_expression_data(duration=20, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):

    start_time = datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S")
    before_time = start_time - timedelta(minutes=duration)
    start_time = datetime.strftime(start_time,"%Y-%m-%d %H:%M:%S")
    before_time = datetime.strftime(before_time,"%Y-%m-%d %H:%M:%S")


    conn = create_connection()
    cursor = conn.cursor()


    cursor.execute("SELECT datetime('now')")
    print("SQLite now (UTC):", cursor.fetchone()[0])

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
        print(len(stress_values))
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
        return "No data available"

# GET LATEST KEYSTROKE DATA
def get_latest_keystroke_data(duration=20, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    start_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    before_time = start_time - timedelta(minutes=duration)
    start_time = datetime.strftime(start_time, "%Y-%m-%d %H:%M:%S")
    before_time = datetime.strftime(before_time, "%Y-%m-%d %H:%M:%S")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT datetime('now')")
    print("SQLite now (UTC):", cursor.fetchone()[0])

    cursor.execute("""
        SELECT * FROM keystroke_summary
        WHERE timestamp BETWEEN ? AND ?
    """, (before_time, start_time))

    rows = cursor.fetchall()

    stress_values = [row[3] for row in rows]  # stress_percentage is the 4th column (index 3)
    stress_array = np.array(stress_values, dtype=np.float32)

    if len(stress_array) > 0:
        mean_value = np.mean(stress_array)
        print(len(stress_values))
        mean_value = round(float(mean_value), 2)
        conn.close()
        return mean_value
    else:
        conn.close()
        return "No data available"

# CREATE RECOMMENDATION LOG TABLE
def create_recommendations_log_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_id TEXT NOT NULL,
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

