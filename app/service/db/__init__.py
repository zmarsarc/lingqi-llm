from aiosqlite import Connection
from . import data, session


async def database() -> Connection:
    return await data.get_database_connection()


async def session_database() -> Connection:
    return await session.get_database_connection()


async def close_database():
    await data.close_database_connection()
    await session.close_database_connection()
