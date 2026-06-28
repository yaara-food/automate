import asyncio

from sqlmodel import SQLModel

from common.db_model.models import Models


async def reset_postgres_schema():

    # from sqlalchemy import text
    # async with DBModel.engine.begin() as conn:
    #     # ⚠️ this will wipe the whole public schema
    #     await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
    #     await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public;"))
    #     await conn.execute(text("SET search_path TO public;"))

    async with Models.to_follow.engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(reset_postgres_schema())
