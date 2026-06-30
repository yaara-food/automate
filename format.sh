#!/usr/bin/env bash
set -euo pipefail

echo "Running isort..."
isort .

echo "Running black..."
black .

echo "Running ruff (lint)..."
#ruff check . --exclude data
#ruff check . --exclude data --fix --unsafe-fixes
ruff check .  --fix


rm -rf .ruff_cache  .idea

find . \( -name "__pycache__" -o -name "*.pyc" \) -prune -exec rm -rf {} +