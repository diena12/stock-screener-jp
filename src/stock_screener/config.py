from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]


def load_environment() -> None:
    load_dotenv(ROOT_DIR / ".env")


def get_output_dir() -> Path:
    load_environment()
    return Path(os.getenv("OUTPUT_DIR", "outputs"))


def get_cache_dir() -> Path:
    load_environment()
    return Path(os.getenv("CACHE_DIR", ".cache/stock-screener-jp"))


def load_rules(name: str) -> dict[str, Any]:
    path = ROOT_DIR / "config" / f"{name}.yaml"
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
