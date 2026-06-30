import asyncio
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func
from sqlmodel import select

from common.db_model.models import Models, RouteModelType


class GitBotStatistics(Models):
    @classmethod
    async def _count_for_day(cls, model: RouteModelType, day: date) -> int:
        start = datetime.combine(day, time.min, tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        statement = (
            select(func.count())
            .select_from(model.table)
            .where(
                model.table.created_at >= start,
                model.table.created_at < end,
            )
        )

        async with model.get_session() as session:
            result = await session.exec(statement)
            return result.one()

    @classmethod
    async def _print_daily_counts(cls, model: RouteModelType, days: int) -> None:
        today = datetime.now(timezone.utc).date()
        print(f"{model.table.__name__} actions")

        for offset in range(days):
            day = today - timedelta(days=offset)
            count = await cls._count_for_day(model, day)
            print(f"{day.isoformat()}: {count}")

    @classmethod
    async def followed_stat(cls, days: int = 3) -> None:
        await cls._print_daily_counts(cls.followed, days)

    @classmethod
    async def unfollowed_stat(cls, days: int = 3) -> None:
        await cls._print_daily_counts(cls.unfollowed, days)


async def main():
    await GitBotStatistics.followed_stat(2)
    await GitBotStatistics.unfollowed_stat(2)


if __name__ == "__main__":
    asyncio.run(main())
