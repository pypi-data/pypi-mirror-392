from __future__ import annotations

from typing import Dict, Literal, TypedDict, Union

from typing_extensions import NotRequired, TypeAlias

from .normalization import NormalizationType

ColumnId: TypeAlias = str

ColumnNumericMap: TypeAlias = Dict[ColumnId, Union[float, int]]

ColumnValuesType: TypeAlias = Literal["number", "seconds"]


class Column(TypedDict):
    id: str
    name: str
    ## TODO: Implement this logic
    valuesType: NotRequired[ColumnValuesType]
    incompatibleNormalizationType: NotRequired[NormalizationType]
    description: NotRequired[str]
