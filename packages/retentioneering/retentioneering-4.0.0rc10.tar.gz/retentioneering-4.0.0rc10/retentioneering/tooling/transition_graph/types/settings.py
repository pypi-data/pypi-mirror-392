from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Settings:
    show_weights: bool | None = None
    show_percents: bool | None = None
    show_nodes_names: bool | None = None
    show_all_edges_for_targets: bool | None = None
    show_nodes_without_links: bool | None = None
    show_edge_info_on_hover: bool | None = None
    open_sidebar_by_default: bool | None = None


@dataclass
class SerializedSettings:
    showEdgesWeightsOnCanvas: bool | None = None
    convertWeightsToPercents: bool | None = None
    showNodesNamesOnCanvas: bool | None = None
    doNotFilterTargetNodes: bool | None = None
    showNodesWithoutEdges: bool | None = None
    showEdgesInfoOnHover: bool | None = None
    openSidebarByDefault: bool | None = None
