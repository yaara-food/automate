import asyncio
from random import shuffle

from common.db_model.models import Models, RouteModelType

# QUERY = "next ecommerce in:name"
# QUERY = "full stack project next in:name"
# QUERY = "full stack project react in:name"
QUERY = "next shop in:name"


class GitHubUserFinder(Models):
    PER_PAGE = 100
    MAX_RESULTS = 3000

    @classmethod
    async def _save_usernames(
        cls,
        model: RouteModelType,
        usernames: list[str] | set[str],
    ) -> None:
        usernames = list({username for username in usernames if username})

        if not usernames:
            return

        await model.add_update(usernames)

        cls.logger.info(f"[{model.table.__name__}] added {len(usernames)} users")

    @classmethod
    async def _fetch_user_page_list(cls, path: str) -> list[str]:
        users = []
        page = 1

        while len(users) < cls.MAX_RESULTS:
            payload, _ = cls.get_json(
                path,
                params={
                    "per_page": cls.PER_PAGE,
                    "page": page,
                },
            )
            payload = payload or []

            if not payload:
                break

            for item in payload:
                if len(users) >= cls.MAX_RESULTS:
                    break

                login = item.get("login")

                if login:
                    users.append(login)

            if len(payload) < cls.PER_PAGE:
                break

            page += 1

        return users

    @classmethod
    async def add_to_blacklist(
        cls,
        username: str,
        *,
        include_followers: bool = True,
        include_following: bool = True,
    ) -> None:
        users = {username}

        if include_followers:
            followers = await cls._fetch_user_page_list(f"/users/{username}/followers")
            users.update(followers)

        if include_following:
            following = await cls._fetch_user_page_list(f"/users/{username}/following")
            users.update(following)

        await cls._save_usernames(cls.blacklist, users)

    @classmethod
    async def by_search(
        cls, max_results: int = 500, to_black_list: bool = False
    ) -> None:
        users = set()
        total = 0
        page = 1

        while total < max_results:
            params = {
                "q": QUERY,
                "sort": "updated",
                "order": "desc",
                "per_page": cls.PER_PAGE,
                "page": page,
            }

            payload, _ = cls.get_json("/search/repositories", params=params)
            items = payload.get("items", [])

            if not items:
                break

            for item in items:
                if total >= max_results:
                    break

                owner = item.get("owner") or {}

                if owner.get("type") == "User" and owner.get("login"):
                    users.add(owner["login"])

                total += 1

            page += 1
        await cls._save_usernames(
            cls.blacklist if to_black_list else cls.to_follow,
            users,
        )

    @classmethod
    async def fetch_stargazers(
        cls, owner: str, repo: str, to_blacklist: bool = False
    ) -> None:
        url = f"/repos/{owner}/{repo}/stargazers"
        users = []

        while url and len(users) < cls.MAX_RESULTS:
            payload, headers = cls.get_json(
                url,
                params={"per_page": cls.PER_PAGE},
            )

            for item in payload:
                if len(users) >= cls.MAX_RESULTS:
                    break

                user = item.get("user") or item
                login = user.get("login")

                if login:
                    users.append(login)

            url = cls.next_link(headers)

        print(len(users))
        await cls._save_usernames(
            cls.blacklist if to_blacklist else cls.to_follow,
            users,
        )

    @classmethod
    async def get_followers(cls, username: str) -> None:
        try:
            followers = await cls._fetch_user_page_list(f"/users/{username}/followers")

            print(username, len(followers))
            await cls._save_usernames(cls.to_follow, followers)

        except Exception as e:
            print(f"e:{e}")

    @classmethod
    async def find_from_follower(cls, batch_size: int = 10) -> None:
        followers = await cls.followers.fetch_rows(as_username=True)
        shuffle(followers)

        selected_followers = [_ for _ in followers if _ not in users_ls][:batch_size]
        print(selected_followers)

        for follower in selected_followers:
            await cls.get_followers(follower)


users_ls = [
    "user",
]

repos: list[tuple[str, str]] = [
    ("owner", "repo"),
]


async def main():
    # await GitHubUserFinder.by_search()

    for owner, repo in repos:
        await GitHubUserFinder.fetch_stargazers(owner, repo)
    #
    # for username in users_ls:
    #     await GitHubUserFinder.get_followers(username)
    #
    # await GitHubUserFinder.get_followers("user")
    await GitHubUserFinder.find_from_follower(100)


if __name__ == "__main__":
    asyncio.run(main())
