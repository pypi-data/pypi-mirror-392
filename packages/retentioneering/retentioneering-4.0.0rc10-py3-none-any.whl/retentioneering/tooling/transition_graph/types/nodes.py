from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, TypedDict, Union

from typing_extensions import NotRequired, TypeAlias

from .column import ColumnNumericMap

NodeId: TypeAlias = str

NodeTargetId: TypeAlias = Literal["suit_node", "positive", "negative", "source"]

NodeType: TypeAlias = str

NodesSortField = Literal["name", "weight", "custom"]

NodesSortOrder = Literal["asc", "desc", "custom"]


class NodeItem(TypedDict):
    id: NodeId
    name: str
    x: NotRequired[float]
    y: NotRequired[float]
    # TODO: It should be enum/literal
    visibilityRule: NotRequired[str]
    size: ColumnNumericMap
    weight: ColumnNumericMap
    targetId: NotRequired[NodeTargetId]
    isGroup: NotRequired[bool]
    isAggregated: NotRequired[bool]
    children: list[NodeId]
    parentNodeId: NotRequired[NodeId]
    description: NotRequired[str]
    customColor: NotRequired[str]


@dataclass
class RecalculationNodeItem:
    id: NodeId
    size: ColumnNumericMap
    weight: ColumnNumericMap
    targetId: NodeTargetId | None


@dataclass
class NodeAggregationData:
    ids: list[NodeId]
    weight: ColumnNumericMap


NodeAggregation: TypeAlias = Dict[NodeId, NodeAggregationData]

NodesCustomColors = Dict[NodeId, str]

NodeTargetEdgeDirection: TypeAlias = Literal["in", "out", "both"]

NodeTargetPosition: TypeAlias = Literal["top-right", "bottom-right", "top-left", "bottom-left"]


class NodeTarget(TypedDict):
    id: NodeTargetId
    name: str
    ignoreThreshold: NotRequired[bool]
    edgeDirection: NotRequired[NodeTargetEdgeDirection]
    position: NotRequired[NodeTargetPosition]
    description: NotRequired[str]


TargetToNodesMap: TypeAlias = Dict[NodeTargetId, Union[NodeId, List[NodeId]]]


class NodePoint(TypedDict):
    x: Union[int, float]
    y: Union[int, float]


NodesPoints: TypeAlias = Dict[NodeId, NodePoint]
