# docker run --name git-bot -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -p 5469:5432 -v postgres_git_bot:/var/lib/postgresql/data -d postgres:18
import os

IS_LOCAL = os.getenv("USER", "1") == os.environ.get("USER_LOCAL")

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ImportError:
    pass


class Config:
    POSTGRES_DATABASE_URL: str = os.environ.get("POSTGRES_DATABASE_URL")
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN")
