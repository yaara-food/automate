import asyncio
from random import shuffle

from common.db_model.models import Models


class GitHubInfo(Models):
    per_page = 100

    @classmethod
    async def _fetch_users_page_list(cls, path: str) -> list[str]:
        page = 1
        users: list[str] = []

        while True:
            items, _ = cls.get_json(
                path,
                params={
                    "per_page": cls.per_page,
                    "page": page,
                },
            )
            items = items or []

            users.extend(user["login"] for user in items if user and user.get("login"))

            if len(items) < cls.per_page:
                break

            page += 1
            cls.sleep()

        return users

    @classmethod
    async def list_following(cls) -> None:
        users = await cls._fetch_users_page_list("/user/following")

        await cls.following.add_update(users)

        cls.logger.info(f"[following] {len(users)} users")

    @classmethod
    async def list_followers(cls) -> None:
        users = await cls._fetch_users_page_list("/user/followers")

        shuffle(users)

        await cls.followers.add_update(users)

        cls.logger.info(f"[followers] {len(users)} users")

    @classmethod
    async def make_unfollow_list(cls) -> None:
        following = await cls.following.fetch_rows(as_username=True)
        followers = await cls.followers.fetch_rows(as_username=True)
        unfollowed = await cls.unfollowed.fetch_rows(as_username=True)
        fail = await cls.fail.fetch_rows(as_username=True)

        followers_set = set(followers)
        unfollowed_set = set(unfollowed)
        fail_set = set(fail)

        to_unfollow = [
            username
            for username in following
            if username not in followers_set
            and username not in unfollowed_set
            and username not in fail_set
        ]

        cls.logger.info(f"[to_unfollow] {len(to_unfollow)} users")

        await cls.to_unfollow.add_update(to_unfollow)

    @classmethod
    async def current(cls) -> None:
        data, _ = cls.get_json("/user")
        data = data or {}

        for key in ["followers", "following"]:
            cls.logger.info(f"[current] {key}: {data.get(key)}")


async def main():
    await GitHubInfo.current()
    # await GitHubInfo.list_following()
    # await GitHubInfo.list_followers()
    # await GitHubInfo.make_unfollow_list()


if __name__ == "__main__":
    asyncio.run(main())
