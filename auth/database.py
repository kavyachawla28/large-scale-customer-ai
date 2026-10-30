
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "users.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'customer')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def create_user(name, email, password_hash, role):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password_hash, role),
        )

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_user(email):
    connection = get_connection()

    try:
        user = connection.execute(
            """
            SELECT id, name, email, password_hash, role
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

        return user

    finally:
        connection.close()


def get_user_by_id(user_id):
    connection = get_connection()

    try:
        user = connection.execute(
            """
            SELECT id, name, email, password_hash, role
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        return user

    finally:
        connection.close()
