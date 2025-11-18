from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from typing_extensions import NotRequired

from .column import Column, ColumnId
from .edges import EdgeItem, EdgesInitialState
from .nodes import NodeItem, NodesSortField, NodesSortOrder, NodeTarget
from .normalization import Normalization, NormalizationId
from .settings import SerializedSettings
from .state_changes import StateChanges
from .threshold import ThresholdValueMap
from .tracker import Tracker


class SerializedNodesState(TypedDict):
    columns: list[Column]
    items: list[NodeItem]
    normalizations: list[Normalization]
    selectedNormalizationId: NormalizationId | None
    selectedWeightsColumnId: ColumnId
    sortField: NodesSortField
    sortOrder: NodesSortOrder
    targets: list[NodeTarget]
    threshold: ThresholdValueMap
    weightsRange: ThresholdValueMap


class SerializedEdgesState(TypedDict):
    columns: list[Column]
    initialState: NotRequired[EdgesInitialState]
    items: list[EdgeItem]
    normalizations: list[Normalization]
    selectedNormalizationId: NormalizationId
    selectedWeightsColumnId: ColumnId
    threshold: ThresholdValueMap
    weightsRange: ThresholdValueMap


@dataclass
class SerializedState:
    tracker: Tracker
    nodes: SerializedNodesState
    edges: SerializedEdgesState
    settings: SerializedSettings
    recalculationChanges: StateChanges = field(default_factory=StateChanges)
    stateChanges: StateChanges = field(default_factory=StateChanges)
    restoreNodesPoints: bool | None = None
    version: str | None = None
