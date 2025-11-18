from __future__ import annotations

from dataclasses import dataclass, field

from .edges import RecalculationEdgeItem
from .nodes import NodeId, RecalculationNodeItem
from .threshold import ThresholdValueMap


@dataclass
class RecalculationResult:
    nodes: dict[NodeId, RecalculationNodeItem] = field(default_factory=dict)
    edges: list[RecalculationEdgeItem] = field(default_factory=list)
    nodesThresholds: ThresholdValueMap = field(default_factory=dict)
    edgesThresholds: ThresholdValueMap = field(default_factory=dict)
    nodesThresholdsMinMax: ThresholdValueMap = field(default_factory=dict)
    edgesThresholdsMinMax: ThresholdValueMap = field(default_factory=dict)
