import sqlite3
from datetime import datetime
import hashlib

class DBHandler:
    def __init__(self, db_name='work_log.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
        ''')
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS work_log (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        self.conn.commit()
        self.add_user_id_column_if_missing()

    def add_user_id_column_if_missing(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(work_log)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE work_log ADD COLUMN user_id INTEGER")
            self.conn.commit()
            print("user_id column added to work_log table.")
        else:
            print("user_id column already exists in work_log table.")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        hashed_password = self.hash_password(password)
        try:
            self.conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            self.conn.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def authenticate_user(self, username, password):
        hashed_password = self.hash_password(password)
        cursor = self.conn.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()
        return user[0] if user else None

    def log_start(self, user_id):
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.conn.execute('INSERT INTO work_log (user_id, start_time) VALUES (?, ?)', (user_id, start_time))
        self.conn.commit()

    def log_end(self, user_id):
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.conn.execute('''
        UPDATE work_log
        SET end_time = ?
        WHERE id = (SELECT MAX(id) FROM work_log WHERE user_id = ?)
        ''', (end_time, user_id))
        self.conn.commit()

    def calculate_salary(self, user_id, hourly_rate=800):
        cursor = self.conn.execute('''
        SELECT start_time, end_time FROM work_log
        WHERE user_id = ? AND end_time IS NOT NULL
        ''', (user_id,))
        total_hours = 0
        for row in cursor:
            start_time = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            total_hours += (end_time - start_time).seconds / 3600
        return total_hours * hourly_rate

def check_table_schema(db_name='work_log.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(work_log)")
    columns = cursor.fetchall()
    conn.close()
    return columns

if __name__ == '__main__':
    db_handler = DBHandler()
    print("Tables created successfully.")
    
    # Verify schema
    columns = check_table_schema()
    print("Columns in work_log table:")
    for column in columns:
        print(column)
