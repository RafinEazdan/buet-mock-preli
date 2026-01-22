import os
import time
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

conn = None


def connect_db():
    global conn
    retries = 5

    while retries > 0:
        try:
            conn = psycopg.connect(
                DATABASE_URL,
                row_factory=dict_row,
                autocommit=True
            )
            print("✅ Database connected")
            return
        except Exception as e:
            print(f"❌ DB connection failed: {e}")
            retries -= 1
            time.sleep(2)

    raise RuntimeError("Could not connect to the database")


def get_db():
    if conn is None:
        connect_db()

    try:
        yield conn
    finally:
        pass  # keep connection alive