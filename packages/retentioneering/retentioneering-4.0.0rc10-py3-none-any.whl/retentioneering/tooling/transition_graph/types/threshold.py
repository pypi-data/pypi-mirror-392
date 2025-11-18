from __future__ import annotations

from typing import Dict, TypedDict, Union

from .column import ColumnId


class ThresholdValue(TypedDict):
    min: float | int
    max: float | int


ThresholdValueMap = Dict[ColumnId, ThresholdValue]

Threshold = Dict[ColumnId, Union[float, int]]

ThresholdWithFallback = Dict[str, Union[ThresholdValue, float, int]]
