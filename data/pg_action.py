import os
import subprocess
from urllib.parse import unquote, urlparse

from common.config import Config


def normalize_url(u: str) -> str:
    return u.replace("postgresql+psycopg", "postgresql")


dump_path = "pg_backup_dump.sql"


def split_url(u: str):
    p = urlparse(u)
    return {
        "user": unquote(p.username) if p.username else "postgres",
        "pwd": unquote(p.password) if p.password else "",
        "host": p.hostname or "localhost",
        "port": str(p.port or 5432),
        "db": p.path.lstrip("/") or "postgres",
    }


def run(cmd: list[str], env=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    r = subprocess.run(cmd, env=e)
    if r.returncode != 0:
        raise SystemExit(f"Command failed: {' '.join(cmd)}")


PG_DUMP = "/opt/homebrew/opt/postgresql@18/bin/pg_dump"


def download_sql(db_url):
    s = split_url(db_url)
    env = {}

    if s["pwd"]:
        env["PGPASSWORD"] = s["pwd"]

    cmd = [
        PG_DUMP,
        "-h",
        s["host"],
        "-p",
        s["port"],
        "-U",
        s["user"],
        "-d",
        s["db"],
        "--no-owner",
        "--no-privileges",
        "--clean",
        "--if-exists",
        "--create",
        "-f",
        dump_path,
    ]

    run(cmd, env)


def reset_target_schema(db_url):
    t = split_url(db_url)
    env = {}
    if t["pwd"]:
        env["PGPASSWORD"] = t["pwd"]
    cmd = [
        "psql",
        "-h",
        t["host"],
        "-p",
        t["port"],
        "-U",
        t["user"],
        "-d",
        t["db"],
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        "DROP SCHEMA IF EXISTS public CASCADE;",
        "-c",
        "CREATE SCHEMA public;",
    ]
    run(cmd, env)


def import_sql(db_url):
    t = split_url(db_url)
    env = {}
    if t["pwd"]:
        env["PGPASSWORD"] = t["pwd"]

    cmd = [
        "psql",
        "-h",
        t["host"],
        "-p",
        t["port"],
        "-U",
        t["user"],
        "-d",
        t["db"],
        "-c",
        "SET session_replication_role = replica;",
        "-f",
        dump_path,
        "-c",
        "SET session_replication_role = DEFAULT;",
    ]
    run(cmd, env)


def run_sql():
    db_source = "postgresql+psycopg://admin:admin@0.0.0.0:5469/postgres"
    db_source = normalize_url(Config.POSTGRES_DATABASE_URL)

    print("SOURCE =", db_source)
    download_sql(db_source)

    # reset_target_schema(db_source)
    # import_sql(db_source)


if __name__ == "__main__":
    run_sql()


"""
docker rm -f git-bot
docker volume rm postgres_git_bot
docker volume create postgres_git_bot

docker run --name git-bot \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -p 5469:5432 \
  -v postgres_git_bot:/var/lib/postgresql \
  -d postgres:18

"""
