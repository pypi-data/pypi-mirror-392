from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Tracker:
    eventstreamIndex: int | None = None
    exportedGraphSource: str | None = None
    hwid: str | None = None
    scope: str | None = None
