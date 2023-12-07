import aiosqlite
from app.config import app_settings

v1_scheme_sesssion = '''CREATE TABLE IF NOT EXISTS sessions(
    uid INTEGER PRIMARY KEY,
    token TEXT NOT NULL UNIQUE,
    ctime TEXT NOT NULL,
    utime TEXT NOT NULL,
    expires INTEGER NOT NULL
);'''

_db: aiosqlite.Connection = None


async def get_database_connection(path: str = app_settings.session_file_path):
    global _db
    if _db is not None:
        return _db

    db = await aiosqlite.connect(path)
    async with db.cursor() as cur:
        await cur.execute(v1_scheme_sesssion)
        await db.commit()

    _db = db
    return _db


async def close_database_connection():
    global _db
    if _db is not None:
        await _db.close()
        _db = None
