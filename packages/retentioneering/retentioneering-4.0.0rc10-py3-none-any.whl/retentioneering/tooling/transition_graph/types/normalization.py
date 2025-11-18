from __future__ import annotations

from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired

NormalizationId = Literal["none", "full", "node"]

NormalizationType = Literal["absolute", "relative"]


class Normalization(TypedDict):
    id: NormalizationId
    name: str
    type: NormalizationType
    description: NotRequired[str]


NormType = Union[Literal["full", "node", "none"], None]
