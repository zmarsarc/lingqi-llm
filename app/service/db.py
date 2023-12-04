import sqlite3

schema_users = '''CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  password TEXT NOT NULL);
'''


def _init_db(cur: sqlite3.Cursor):
    cur.execute(schema_users)


def _make_db_connect(path: str = '/app/data.db'):
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
