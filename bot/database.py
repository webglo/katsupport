import aiosqlite
from config import CONFIG

async def init_db():
    async with aiosqlite.connect(CONFIG.DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS modmail_blacklist (
                member_id INTEGER PRIMARY KEY,
                reason TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ticket_blacklist (
                member_id INTEGER PRIMARY KEY,
                reason TEXT
            )
        """)
        await db.commit()

async def is_blacklisted(member_id: int, blacklist_type: str) -> bool:
    async with aiosqlite.connect(CONFIG.DATABASE_PATH) as db:
        async with db.execute(
            f"SELECT 1 FROM {blacklist_type}_blacklist WHERE member_id = ?",
            (member_id,)
        ) as cursor:
            return await cursor.fetchone() is not None

async def add_to_blacklist(member_id: int, reason: str, blacklist_type: str):
    async with aiosqlite.connect(CONFIG.DATABASE_PATH) as db:
        await db.execute(
            f"INSERT OR REPLACE INTO {blacklist_type}_blacklist (member_id, reason) VALUES (?, ?)",
            (member_id, reason)
        )
        await db.commit()

async def remove_from_blacklist(member_id: int, blacklist_type: str):
    async with aiosqlite.connect(CONFIG.DATABASE_PATH) as db:
        await db.execute(
            f"DELETE FROM {blacklist_type}_blacklist WHERE member_id = ?",
            (member_id,)
        )
        await db.commit()

async def get_blacklist_reason(member_id: int, blacklist_type: str) -> str:
    async with aiosqlite.connect(CONFIG.DATABASE_PATH) as db:
        async with db.execute(
            f"SELECT reason FROM {blacklist_type}_blacklist WHERE member_id = ?",
            (member_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None