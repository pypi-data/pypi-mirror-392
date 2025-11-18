from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, TypedDict

from typing_extensions import NotRequired, TypeAlias

from .column import ColumnNumericMap
from .nodes import NodeId

EdgeId: TypeAlias = str

EdgesGroupId: TypeAlias = str


class EdgeItem(TypedDict):
    id: EdgeId
    sourceNodeId: NodeId
    targetNodeId: NodeId
    size: ColumnNumericMap
    weight: ColumnNumericMap
    aggregatedEdges: list[EdgeId]
    description: NotRequired[str]
    customColor: NotRequired[str]


class EdgesInitialStateMutated(TypedDict):
    disabledNodes: list[NodeId]
    items: list[EdgeItem]


class EdgesInitialState(TypedDict):
    defaultItems: list[EdgeItem]
    mutated: EdgesInitialStateMutated


@dataclass
class RecalculationEdgeItem:
    id: EdgeId
    sourceNodeId: NodeId
    targetNodeId: NodeId
    size: ColumnNumericMap
    weight: ColumnNumericMap


@dataclass
class EdgeAggregationData:
    ids: list[EdgeId]
    weight: ColumnNumericMap
    size: ColumnNumericMap


EdgeAggregation: TypeAlias = Dict[EdgesGroupId, EdgeAggregationData]

EdgesCustomColors = Dict[Tuple[NodeId, NodeId], str]
