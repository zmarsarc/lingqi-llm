import aiosqlite
from app.config import app_settings

v1_schema_users = '''CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  salt TEXT NOT NULL,
  ctime TEXT NOT NULL);
'''

v2_schema_chat = '''CREATE TABLE IF NOT EXISTS chat_history(
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  ctime TEXT NOT NULL);
'''

_db: aiosqlite.Connection = None


async def get_database_connection(path: str = app_settings.data_file_path):
    global _db

    if _db is not None:
        return _db

    db = await aiosqlite.connect(path)
    async with db.cursor() as cur:
        await cur.execute(v1_schema_users)
        await cur.execute(v2_schema_chat)
        await db.commit()

    _db = db
    return db


async def close_database_connection():
    global _db

    if _db is not None:
        await _db.close()
        _db = None
