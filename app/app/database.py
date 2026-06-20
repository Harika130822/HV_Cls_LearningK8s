import os
import re
import time
from urllib.parse import quote_plus

import psycopg2
from psycopg2.extras import RealDictCursor


def database_url():
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "appdb")
    user = os.getenv("DB_USER", "appuser")
    password = os.getenv("DB_PASSWORD", "apppassword")

    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{quote_plus(name)}"
    )


def get_connection():
    return psycopg2.connect(database_url(), connect_timeout=3)


def ensure_schema(retries=30, delay=2):
    sql = """
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(80) UNIQUE NOT NULL,
      display_name VARCHAR(80) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS messages (
      id SERIAL PRIMARY KEY,
      author VARCHAR(60) NOT NULL,
      body TEXT NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    last_error = None
    for _ in range(retries):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
            return
        except psycopg2.Error as exc:
            last_error = exc
            time.sleep(delay)

    raise RuntimeError("Database schema could not be initialized") from last_error


def normalize_username(display_name):
    username = re.sub(r"[^a-z0-9]+", "-", display_name.lower()).strip("-")
    return username[:80] or "student"


def serialize_row(row):
    result = dict(row)
    created_at = result.get("created_at")
    if hasattr(created_at, "isoformat"):
        result["created_at"] = created_at.isoformat()
    return result


def list_users():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, username, display_name, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT 30;
                """
            )
            return cur.fetchall()


def create_user(display_name):
    username = normalize_username(display_name)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO users (username, display_name)
                VALUES (%s, %s)
                ON CONFLICT (username)
                DO UPDATE SET display_name = EXCLUDED.display_name
                RETURNING id, username, display_name, created_at;
                """,
                (username, display_name),
            )
            return cur.fetchone()


def count_users():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            return cur.fetchone()[0]


def list_messages():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, author, body, created_at
                FROM messages
                ORDER BY created_at DESC
                LIMIT 30;
                """
            )
            return cur.fetchall()


def create_message(author, body):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (author, body) VALUES (%s, %s);",
                (author, body),
            )


def delete_message(message_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM messages WHERE id = %s;", (message_id,))


def count_messages():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM messages;")
            return cur.fetchone()[0]
