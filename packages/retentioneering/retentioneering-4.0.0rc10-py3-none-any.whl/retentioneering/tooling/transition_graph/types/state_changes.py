from __future__ import annotations

from dataclasses import dataclass, field

from .edges import EdgeAggregation
from .nodes import NodeAggregation, NodeId
from .threshold import ThresholdValueMap


@dataclass
class StateChanges:
    disabledNodes: list[NodeId] = field(default_factory=list)
    nodesThreshold: ThresholdValueMap = field(default_factory=dict)
    edgesThreshold: ThresholdValueMap = field(default_factory=dict)
    nodesAggregation: list[NodeAggregation] = field(default_factory=list)
    edgesAggregation: list[EdgeAggregation] = field(default_factory=list)
