from typing import Any


class BaseRepository:
    """Simple repository wrapper for modular service access."""

    def __init__(self, storage: dict[int, dict] | None = None):
        self.storage = storage or {}

    def list(self):
        return list(self.storage.values())

    def get(self, item_id: int):
        return self.storage.get(item_id)

    def create(self, item_id: int, payload: dict[str, Any]):
        self.storage[item_id] = payload
        return payload
