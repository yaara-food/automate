from sqlmodel import func, select

from common.db_model.models import Models, RouteModelType


class GitHubFollowActions(Models):

    @classmethod
    def _request_follow_state(
        cls,
        username: str,
        *,
        method: str,
        success_codes: tuple[int, ...],
        fail_codes: tuple[int, ...],
    ) -> bool:
        response = cls.request(
            f"/user/following/{username}",
            method=method,
            success_codes=success_codes,
            fail_codes=fail_codes,
        )
        return response is not None

    @classmethod
    async def follow_user(cls, username: str) -> bool:
        return cls._request_follow_state(
            username=username,
            method="PUT",
            success_codes=(204, 200),
            fail_codes=(404, 422),
        )

    @classmethod
    async def unfollow_user(cls, username: str) -> bool:
        return cls._request_follow_state(
            username=username,
            method="DELETE",
            success_codes=(204, 200, 404),
            fail_codes=(422,),
        )

    @classmethod
    async def _build_queue(
        cls,
        source_model: RouteModelType,
        done_model: RouteModelType,
        batch_size: int,
    ) -> list[str]:
        username = source_model.table.username

        stmt = (
            select(username)
            .where(username.not_in(select(done_model.table.username)))
            .where(username.not_in(select(cls.fail.table.username)))
            .where(username.not_in(select(cls.blacklist.table.username)))
            .order_by(func.random())
            .limit(batch_size)
        )

        async with source_model.get_session() as session:
            result = await session.exec(stmt)
            queue = list(result.all())
            return queue

    @classmethod
    async def _run_batch(
        cls,
        *,
        batch_size: int,
        source_model: RouteModelType,
        done_model: RouteModelType,
        action,
        ok_label: str,
    ) -> None:
        queue = await cls._build_queue(
            source_model=source_model, done_model=done_model, batch_size=batch_size
        )

        cls.logger.info(f"[batch] {len(queue)} users")

        for username in queue:
            try:
                ok = await action(username)

                if ok:
                    cls.logger.info(f"[{ok_label}] @{username}")
                    await done_model.add_update(username)
                else:
                    cls.logger.warning(f"[fail] @{username}")
                    await cls.fail.add_update(username)

            except Exception as e:
                cls.logger.exception(f"[error] @{username}: {e}")

            cls.sleep()

    @classmethod
    async def follow_batch(cls, batch_size: int = 10) -> None:
        await cls._run_batch(
            batch_size=batch_size,
            source_model=cls.to_follow,
            done_model=cls.followed,
            action=cls.follow_user,
            ok_label="followed",
        )

    @classmethod
    async def unfollow_batch(cls, batch_size: int = 10) -> None:
        await cls._run_batch(
            batch_size=batch_size,
            source_model=cls.to_unfollow,
            done_model=cls.unfollowed,
            action=cls.unfollow_user,
            ok_label="unfollowed",
        )
