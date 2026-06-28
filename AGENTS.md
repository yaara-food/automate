# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python GitHub automation bot backed by PostgreSQL.

- `run.py` is the local long-running entry point for follow/unfollow batches.
- `actions/` contains operational scripts: `user_actions.py`, `find_users.py`, `info.py`, and `statistics.py`.
- `common/` contains shared configuration, database models, GitHub request helpers, logging, and errors.
- `data/` contains database setup/import helpers and local operational data such as `db.json`.
- `.github/workflows/` contains scheduled GitHub Actions for follow and unfollow runs.

There is currently no committed `tests/` directory.

## Build, Test, and Development Commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create and prepare a local Python environment.

```bash
python run.py
```

Run the local bot loop. Use carefully because it calls GitHub and updates the database.

```bash
python data/create_tables.py
python data/create_data.py
python actions/statistics.py
```

Create tables, import seed usernames, and print recent action counts.

```bash
./format.sh
```

Runs `isort`, `black`, and `ruff check . --exclude data --fix`.

## Coding Style & Naming Conventions

Use Python 3.14 style with 4-space indentation. Use `snake_case` for functions and variables, `PascalCase` for classes, and lowercase module names. Keep GitHub API calls in shared mixin-based classes such as `GitHubRequestMixin`; avoid duplicating request/rate-limit logic in action scripts.

## Testing Guidelines

No test framework is configured yet. When adding tests, use `pytest`, place tests under `tests/`, and name files `test_*.py`. Prioritize database helpers, queue filtering, GitHub API status handling, and statistics counts. Mock GitHub requests and database sessions where possible.

## Commit & Pull Request Guidelines

Recent commits are short, for example `split cron`, `add git action`, and `add statistics and clean. request mixin`. Keep messages concise but specific, preferably imperative.

Pull requests should include a short summary, commands run, workflow changes, required secrets, and any impact on username tables.

## Security & Configuration Tips

Do not commit `.env`, tokens, SQL dumps, or production state. Configure `POSTGRES_DATABASE_URL` and `GIT_BOT_GITHUB_TOKEN` as GitHub repository secrets. Local code reads `POSTGRES_DATABASE_URL` and `GITHUB_TOKEN` from the environment.
