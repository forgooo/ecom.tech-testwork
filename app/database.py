import asyncpg
from app.config import get_settings
from typing import Optional, List, Tuple, Dict, Any


_pool: Optional[asyncpg.Pool] = None # глобал пул 


async def init_db() -> asyncpg.Pool:
    global _pool
    settings = get_settings()
    _pool = await asyncpg.create_pool(
        host = settings.DB_HOST,
        port = settings.DB_PORT,
        user = settings.DB_USER,
        password = settings.DB_PASSWORD,
        database = settings.DB_NAME,
        min_size = settings.DB_POOL_MIN_SIZE,
        max_size = settings.DB_POOL_MAX_SIZE,
    )
    #print('pool created')
    return _pool


def get_pool():
    global _pool
    if _pool is None:
        raise RuntimeError('Пул дб не инициализирован')
    return _pool


async def close_db() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        #print('pool closed')


async def get_connection():
    pool = get_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)


async def execute_query(query: str, *args) -> list:
    pool = get_pool()
    conn = await pool.acquire()
    try:
        return await conn.fetch(query, *args)
    finally:
        await get_pool().release(conn)

    
async def execute_update(query: str, *args) -> str:
    pool = get_pool()
    conn = await pool.acquire()
    try:
        return await conn.execute(query, *args)
    finally:
        await get_pool().release(conn)


async def execute_many(query: str, args_list: list) -> None:
    pool = get_pool()
    conn = await pool.acquire()
    try:
        await conn.executemany(query, args_list)
    finally:
        await get_pool().release(conn)


async def execute_query_single(query: str, *args):
    conn = await get_pool().acquire()
    try:
        result = await conn.fetchrow(query, *args)
        return dict(result) if result else None
    finally:
        await get_pool().release(conn)