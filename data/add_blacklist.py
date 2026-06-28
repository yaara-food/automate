import asyncio

from actions.find_users import GitHubUserFinder
from data import read_json

DB_DATA = read_json("db.json")


async def main():
    for repo in DB_DATA.get("repos"):
        await GitHubUserFinder.fetch_stargazers(
            DB_DATA.get("owner"), repo, to_blacklist=True
        )

    for username in DB_DATA.get("users"):
        await GitHubUserFinder.add_to_blacklist(username)


if __name__ == "__main__":
    asyncio.run(main())
