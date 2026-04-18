import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConfig:
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    DB_NAME = os.getenv("DB_NAME", "mdm_db.sqlite")

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DB_NAME)

    @classmethod
    @contextmanager
    def get_db_cursor(cls, commit=False):
        conn = cls.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def init_database(cls):
        with cls.get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action VARCHAR(50) NOT NULL,
                    table_name VARCHAR(50),
                    record_id INTEGER,
                    old_value TEXT,
                    new_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS master_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_set_name VARCHAR(100) NOT NULL,
                    data_type VARCHAR(50) NOT NULL,
                    data_value TEXT NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_quality_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id INTEGER,
                    data_set_name VARCHAR(100),
                    validation_type VARCHAR(50),
                    is_valid INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)