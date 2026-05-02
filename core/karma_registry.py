"""
Singleton registry that loads karma_categories.json once at import time
and exposes fast O(1) lookup by action_id.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "karma_categories.json"


class _KarmaRegistry:
    def __init__(self) -> None:
        with _DATA_FILE.open(encoding="utf-8") as fh:
            raw: dict[str, Any] = json.load(fh)

        self._categories: list[dict[str, Any]] = raw["categories"]

        # Build flat action index: action_id → {category_meta, action_data}
        self._index: dict[str, dict[str, Any]] = {}
        for cat in self._categories:
            cat_meta = {
                "category_id": cat["id"],
                "category_name": cat["name"],
                "category_description": cat["description"],
            }
            for action in cat["positive"] + cat["negative"]:
                self._index[action["id"]] = {**cat_meta, **action}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_action(self, action_id: str) -> dict[str, Any] | None:
        """Return the full action dict (including category meta) or None."""
        return self._index.get(action_id)

    def action_exists(self, action_id: str) -> bool:
        return action_id in self._index

    @property
    def categories(self) -> list[dict[str, Any]]:
        return self._categories

    @property
    def all_action_ids(self) -> list[str]:
        return list(self._index.keys())


# Module-level singleton — loaded once at startup
karma_registry = _KarmaRegistry()
