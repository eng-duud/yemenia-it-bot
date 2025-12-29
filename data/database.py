import sqlite3
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Levels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
            ''')
            # Semesters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS semesters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level_id INTEGER,
                    name TEXT,
                    FOREIGN KEY (level_id) REFERENCES levels (id)
                )
            ''')
            # Subjects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    semester_id INTEGER,
                    name TEXT,
                    FOREIGN KEY (semester_id) REFERENCES semesters (id)
                )
            ''')
            # Content table (Summaries, Handouts, Links)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER,
                    type TEXT, -- 'summary', 'handout', 'link'
                    title TEXT,
                    file_id TEXT, -- Telegram file_id for PDFs
                    url TEXT, -- For links
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
            ''')
            
            # Insert default levels if not exist
            cursor.execute("SELECT COUNT(*) FROM levels")
            if cursor.fetchone()[0] == 0:
                levels = [("المستوى الأول",), ("المستوى الثاني",), ("المستوى الثالث",), ("المستوى الرابع",)]
                cursor.executemany("INSERT INTO levels (name) VALUES (?)", levels)
                
                # Insert default semesters for each level
                cursor.execute("SELECT id FROM levels")
                level_ids = cursor.fetchall()
                for level_id in level_ids:
                    semesters = [(level_id[0], "الترم الأول"), (level_id[0], "الترم الثاني")]
                    cursor.executemany("INSERT INTO semesters (level_id, name) VALUES (?, ?)", semesters)
            
            conn.commit()

    def add_user(self, user_id, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
            conn.commit()

    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            return [row[0] for row in cursor.fetchall()]

    def get_levels(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM levels")
            return cursor.fetchall()

    def get_semesters(self, level_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM semesters WHERE level_id = ?", (level_id,))
            return cursor.fetchall()

    def get_subjects(self, semester_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM subjects WHERE semester_id = ?", (semester_id,))
            return cursor.fetchall()

    def add_subject(self, semester_id, name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subjects (semester_id, name) VALUES (?, ?)", (semester_id, name))
            conn.commit()
            return cursor.lastrowid

    def add_content(self, subject_id, content_type, title, file_id=None, url=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO content (subject_id, type, title, file_id, url) VALUES (?, ?, ?, ?, ?)",
                (subject_id, content_type, title, file_id, url)
            )
            conn.commit()

    def get_content(self, subject_id, content_type):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, file_id, url FROM content WHERE subject_id = ? AND type = ?",
                (subject_id, content_type)
            )
            return cursor.fetchall()

    def delete_content(self, content_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM content WHERE id = ?", (content_id,))
            conn.commit()
            
    def delete_subject(self, subject_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM content WHERE subject_id = ?", (subject_id,))
            cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            conn.commit()
