from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EnvId = Literal["classic", "colab"]


@dataclass
class Env:
    id: EnvId | None = None
    serverId: str | None = None
    kernelId: str | None = None
    libVersion: str | None = None
