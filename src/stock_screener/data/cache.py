from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class JsonCache:
    def __init__(self, cache_dir: Path, ttl_hours: int = 24) -> None:
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe_key = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Any | None:
        path = self._path(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        created_at = datetime.fromisoformat(payload["created_at"])
        if datetime.now(timezone.utc) - created_at > self.ttl:
            return None
        return payload["data"]

    def set(self, key: str, data: Any) -> None:
        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self._path(key).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
