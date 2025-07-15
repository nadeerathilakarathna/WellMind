import sqlite3
from datetime import datetime
import pandas as pd
import os

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
def create_preferences_tables():
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
def import_preferences_from_excel(excel_path="assets/documents/preferences.xlsx"):
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
def create_user_preferences_mapping_table():
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
def get_all_categories():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, category_name FROM preferences_category ORDER BY category_name")
    categories = cursor.fetchall()
    conn.close()
    return categories

# FETCH CATEGORY WISE PREFERENCES SQL QUERY
def get_preferences_by_category(category_id):
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
def get_preference_id_by_name(name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT preference_id FROM preferences WHERE preference_name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# SAVE USER SELECTED PREFERENCES ON THE DATABASE
def insert_user_preference_mapping(user_id, preference_id):
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
def get_user_preferences_by_user_id(user_id):
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
