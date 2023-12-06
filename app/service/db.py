import sqlite3
from app.config import app_settings

schema_users = '''CREATE table if not EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  salt TEXT NOT NULL,
  ctime TEXT NOT NULL);
'''

schema_chat = '''CREATE TABLE if NOT EXISTS chat_history(
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  ctime TEXT NOT NULL);
'''


def _init_db(cur: sqlite3.Cursor):
    cur.execute(schema_users)
    cur.execute(schema_chat)


def _make_db_connect(path: str = app_settings.data_file_path):
    conn = sqlite3.connect(path)
    _init_db(conn.cursor())
    conn.commit()
    conn.row_factory = sqlite3.Row

    def getter():
        return conn
    return getter


_get_db_connect = _make_db_connect()


def database():
    return _get_db_connect()
