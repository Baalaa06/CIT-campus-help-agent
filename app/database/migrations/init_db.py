"""Create all tables and verify they exist."""
import asyncio

from app.database.connection import Base, engine
from app.database.models import (  # noqa: F401 — imports register metadata
    ApprovalRequest,
    ConversationHistory,
    Document,
    Feedback,
    QueryLog,
)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def verify_tables() -> list[str]:
    from sqlalchemy import inspect, text

    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
    return tables


async def init_db() -> None:
    await create_tables()
    tables = await verify_tables()
    print(f"[DB] Tables ready: {tables}")


if __name__ == "__main__":
    asyncio.run(init_db())
