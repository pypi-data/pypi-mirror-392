import json
from typing import Any


def load_config(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
