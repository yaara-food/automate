import json
from pathlib import Path


def read_json(filename: str):
    path = Path(__file__).parent / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filename: str, data):
    path = Path(__file__).parent / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
