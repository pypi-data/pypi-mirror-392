from __future__ import annotations

import json
import os
import random
import string
import warnings
from dataclasses import asdict
from typing import Any, Dict, List, Literal, MutableMapping, Sequence, Union, cast

import networkx as nx
import numpy as np
import pandas as pd
from IPython.core.display import HTML, display
from nanoid import generate

from retentioneering import RETE_CONFIG, __version__
from retentioneering.backend import ServerManager
from retentioneering.backend.tracker import collect_data_performance, time_performance
from retentioneering.edgelist import Edgelist
from retentioneering.eventstream.types import EventstreamType
from retentioneering.nodelist import Nodelist
from retentioneering.nodelist.nodelist import (
    IS_AGGREGATED_COL,
    IS_DISABLED_COL,
    IS_GROUP_COL,
    IS_PINNED_COL,
    NAME_COL,
    PARENT_ID_COL,
)
from retentioneering.templates.transition_graph import TransitionGraphRenderer

from .types import (
    Column,
    EdgeId,
    EdgeItem,
    EdgesCustomColors,
    NodeId,
    NodeItem,
    NodePoint,
    NodesCustomColors,
    NodesPoints,
    NodeTarget,
    NodeTargetId,
    Normalization,
    NormType,
    RecalculationEdgeItem,
    RecalculationNodeItem,
    RecalculationResult,
    SerializedEdgesState,
    SerializedNodesState,
    SerializedSettings,
    SerializedState,
    Settings,
    StateChanges,
    TargetToNodesMap,
    ThresholdValueMap,
    ThresholdWithFallback,
    Tracker,
    Weight,
)

SESSION_ID_COL = "session_id"


class TransitionGraph:
    """
    A class that holds methods for transition graph visualization.

    Parameters
    ----------
    eventstream: EventstreamType
        Source eventstream.


    See Also
    --------
    .Eventstream.transition_graph : Call TransitionGraph tool as an eventstream method.
    .Eventstream.transition_matrix : Matrix representation of transition graph.
    .EventstreamSchema : Schema of eventstream columns, that could be used as weights.
    .TransitionGraph.plot : Interactive transition graph visualization.


    Notes
    -----
    See :doc:`transition graph user guide</user_guides/transition_graph>` for the details.

    """

    DEFAULT_GRAPH_URL = "https://static.server.retentioneering.com/package/@rete/transition-graph/version/4/dist/transition-graph.umd.js"

    _weights: MutableMapping[str, str] | None

    _nodes_norm_type: NormType
    _edges_norm_type: NormType

    _nodes_threshold: ThresholdValueMap = {}
    _edges_threshold: ThresholdValueMap = {}

    _recalculation_result: EventstreamType

    _allowed_targets: list[NodeTarget] = [
        NodeTarget(
            id="positive",
            name="Positive",
            ignoreThreshold=True,
            edgeDirection="in",
            position="top-right",
        ),
        NodeTarget(
            id="negative",
            name="Negative",
            ignoreThreshold=True,
            edgeDirection="in",
            position="bottom-right",
        ),
        NodeTarget(
            id="source",
            name="Source",
            ignoreThreshold=False,
            edgeDirection="both",
            position="top-left",
        ),
    ]

    _allowed_normalizations: list[Normalization] = [
        Normalization(id="none", name="none", type="absolute"),
        Normalization(id="full", name="full", type="relative"),
        Normalization(id="node", name="node", type="relative"),
    ]

    @property
    def graph_url(self) -> str:
        env_url: str = os.getenv("RETE_TRANSITION_GRAPH_URL", "")
        return env_url if env_url else self.DEFAULT_GRAPH_URL

    @property
    def nodes_thresholds(self) -> ThresholdValueMap:
        return self._nodes_threshold

    @nodes_thresholds.setter
    def nodes_thresholds(self, value: ThresholdValueMap) -> None:
        if self._check_thresholds_for_norm_type(value=value, norm_type=self.nodes_norm_type):
            self._nodes_threshold = value

    @property
    def edges_thresholds(self) -> ThresholdValueMap:
        return self._edges_threshold

    @edges_thresholds.setter
    def edges_thresholds(self, value: ThresholdValueMap) -> None:
        if self._check_thresholds_for_norm_type(value=value, norm_type=self.edges_norm_type):
            self._edges_threshold = value

    @staticmethod
    def _check_thresholds_for_norm_type(value: ThresholdValueMap, norm_type: NormType) -> bool:
        values: List[Union[int, float]] = [val for key in value.values() for val in key.values()]  # type: ignore

        if norm_type is None:
            if not all(map(lambda x: x is None or x >= 0, values)):  # type: ignore
                raise ValueError(f"For normalization type {norm_type} all thresholds must be positive or None")
        else:
            if not all(map(lambda x: x is None or 0 <= x <= 1, values)):  # type: ignore
                raise ValueError(f"For normalization type {norm_type} all thresholds must be between 0 and 1 or None")

        return True

    @time_performance(
        scope="transition_graph",
        event_name="init",
    )
    def __init__(
        self,
        eventstream: EventstreamType,  # graph: dict,  # preprocessed graph
    ) -> None:
        from retentioneering.eventstream.eventstream import Eventstream

        sm = ServerManager()
        self.sm = sm

        self.server = sm.create_server()
        self.bridge_id = sm.widget.bridge_id if sm.widget else ""

        self.server.register_action("recalculate", lambda n: self._on_recalc_request(n))

        self.server.register_action("test", lambda n: self._on_test_request(n))

        self.eventstream: Eventstream = eventstream  # type: ignore

        self.event_col = self.eventstream.schema.event_name
        self.event_time_col = self.eventstream.schema.event_timestamp
        self.user_col = self.eventstream.schema.user_id

        self.weight_cols = self._define_weight_cols(None)

        self.nodes_weight_col = self.eventstream.schema.user_id
        self.edges_weight_col = self.eventstream.schema.user_id

        # TODO: WIP Layout experiments
        self.spring_layout_config = {"k": 0.1, "iterations": 300, "nx_threshold": 1e-4}

        self.render: TransitionGraphRenderer = TransitionGraphRenderer()

        self._recalculation_result = eventstream

        self.targets: TargetToNodesMap = {}

        self.nodes_weights_range: ThresholdValueMap = {}
        self.edges_weights_range: ThresholdValueMap = {}

        self.nodes_custom_colors: NodesCustomColors = {}
        self.edges_custom_colors: EdgesCustomColors = {}

        self.settings = Settings(
            show_weights=RETE_CONFIG.transition_graph.show_weights,
            show_percents=RETE_CONFIG.transition_graph.show_percents,
            show_nodes_names=RETE_CONFIG.transition_graph.show_nodes_names,
            show_all_edges_for_targets=RETE_CONFIG.transition_graph.show_all_edges_for_targets,
            show_nodes_without_links=RETE_CONFIG.transition_graph.show_nodes_without_links,
            show_edge_info_on_hover=RETE_CONFIG.transition_graph.show_edge_info_on_hover,
            open_sidebar_by_default=RETE_CONFIG.transition_graph.open_sidebar_by_default,
        )

        self.width: str | int | float = RETE_CONFIG.transition_graph.width
        self.height: str | int | float = RETE_CONFIG.transition_graph.height

        self.nodes_points: NodesPoints = {}

        self._state_changes = StateChanges()
        self._recalculation_changes = StateChanges()

    @property
    @time_performance(
        scope="transition_graph",
        event_name="recalculation_result",
    )
    def recalculation_result(self) -> EventstreamType:
        """
        Export an eventstream after GUI actions that affect eventstream.

        Returns
        -------
        EventstreamType
            The modified event stream.

        Notes
        -----
        Renaming groups, nodes, and nested nodes in the GUI will not affect the resulting eventstream.
        The default group and node names will be returned.
        """
        return self._recalculation_result

    def _define_weight_cols(self, custom_weight_cols: list[str] | None) -> list[str]:
        weight_cols = [
            self.eventstream.schema.event_id,
            self.eventstream.schema.user_id,
        ]
        if SESSION_ID_COL in self.eventstream.schema.custom_cols:
            weight_cols.append(SESSION_ID_COL)
        if isinstance(custom_weight_cols, list):
            for col in custom_weight_cols:
                if col not in weight_cols:
                    if col not in self.eventstream.schema.custom_cols:
                        raise ValueError(f"Custom weights column {col} not found in eventstream schema")
                    else:
                        weight_cols.append(col)
        return weight_cols

    @property
    def weights(self) -> MutableMapping[str, str] | None:
        return self._weights

    @weights.setter
    def weights(self, value: MutableMapping[str, str] | None) -> None:
        available_cols = self.__get_nodelist_cols()

        if value and ("edges" not in value or "nodes" not in value):
            raise ValueError("Allowed only: %s" % {"edges": "col_name", "nodes": "col_name"})

        if value and (value["edges"] not in available_cols or value["nodes"] not in available_cols):
            raise ValueError("Allowed only: %s" % {"edges": "col_name", "nodes": "col_name"})

        self._weights = value

    @property
    def edges_norm_type(self) -> NormType:
        return self._edges_norm_type

    @edges_norm_type.setter
    def edges_norm_type(self, edges_norm_type: NormType) -> None:
        allowed_edges_norm_types: list[str | None] = [None, "full", "node"]
        if edges_norm_type in allowed_edges_norm_types:
            self._edges_norm_type = edges_norm_type
        else:
            raise ValueError("Norm type should be one of: %s" % allowed_edges_norm_types)

    @property
    def nodes_norm_type(self) -> NormType:
        return self._nodes_norm_type

    @nodes_norm_type.setter
    def nodes_norm_type(self, nodes_norm_type: NormType) -> None:
        if nodes_norm_type is not None:
            warnings.warn(f"Currently nodes_norm_type allowed to be None only")
        self._nodes_norm_type = None

    @staticmethod
    def _extract_nodes_points_from_serialized_state(serialized_state: SerializedState) -> NodesPoints:
        result: NodesPoints = {}

        for node in serialized_state.nodes["items"]:
            x = node.get("x")
            y = node.get("y")
            if x is not None and y is not None:
                result[node["id"]] = NodePoint(x=x, y=y)

        return result

    def make_nodelist_from_serialized_state(self, serialized_state: SerializedState) -> pd.DataFrame:
        nodelist_data: List[Dict[str, Any]] = []
        weight_cols = self.weight_cols

        for node in serialized_state.nodes["items"]:
            new_node: Dict[str, Any] = {self.event_col: node["id"]}
            # TODO: WIP Refactor me
            visibility_rule = node.get("visibilityRule", None)
            new_node[IS_DISABLED_COL] = visibility_rule == "disabled"
            new_node[IS_PINNED_COL] = visibility_rule == "pinned"
            new_node[PARENT_ID_COL] = node.get("parentNodeId", None)
            new_node[IS_GROUP_COL] = node.get("isGroup", False)
            new_node[IS_AGGREGATED_COL] = node.get("isAggregated", False)
            name = node.get("name")
            new_node[NAME_COL] = name if name != new_node[self.event_col] else new_node[self.event_col]

            weights: Dict[str, float] = node.get("weight", {})

            for weight_col in weight_cols:
                weight = weights.get(weight_col, None)
                if weight is not None:
                    new_node[weight_col] = weight

            nodelist_data.append(new_node)

        return pd.DataFrame(nodelist_data)

    def _on_test_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"status": "ok", "message": "Test request received"}

    def _on_recalc_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            t = json.loads(payload["recalcjson"])
            serialized_state: SerializedState = self.__build_serialized_state_from_unknown_data(t)
        except Exception:
            raise Exception("Invalid recalculate data")

        try:
            self.nodes_points = self._extract_nodes_points_from_serialized_state(serialized_state)

            self._state_changes = serialized_state.stateChanges
            self._recalculation_changes = serialized_state.recalculationChanges

            self.nodes_thresholds = serialized_state.stateChanges.nodesThreshold
            self.edges_thresholds = serialized_state.stateChanges.edgesThreshold

            new_nodelist = self.make_nodelist_from_serialized_state(serialized_state)
            self._recalculation_result = self.__apply_nodelist(new_nodelist)

            nodes_items = self._prepare_nodes(nodelist=self.nodelist.nodelist_df)
            edgelist = self.edgelist.get_filtered_edges()
            edgelist["type"] = "suit"

            recalculation_response = self._build_recalculation_response(
                serialized_state=serialized_state,
                nodes=nodes_items,
                edges=self._prepare_edges(edgelist=edgelist, nodes_items=nodes_items),
            )

            # noinspection PyTypeChecker
            # see https://youtrack.jetbrains.com/issue/PY-76059/Incorrect-Type-warning-with-asdict-and-Dataclass
            return asdict(recalculation_response)
        except Exception as err:
            raise ValueError("error! %s" % err)

    def _build_recalculation_response(
        self, serialized_state: SerializedState, nodes: list[NodeItem], edges: list[EdgeItem]
    ) -> RecalculationResult:
        renamed_nodes = {}
        for node_item in serialized_state.nodes["items"]:
            renamed_nodes[node_item["id"]] = node_item["name"]

        node_edge_map: dict[str, EdgeId] = {}
        node_id_name_mapping: dict[NodeId, str] = {node["id"]: node["name"] for node in serialized_state.nodes["items"]}
        node_name_id_mapping: dict[NodeId, str] = {node["name"]: node["id"] for node in serialized_state.nodes["items"]}
        for edge in serialized_state.edges["items"]:
            node_edge_map[
                f'{[node_id_name_mapping[edge["sourceNodeId"]]]}, {node_id_name_mapping[edge["targetNodeId"]]}'
            ] = edge["id"]

        response_nodes: dict[NodeId, RecalculationNodeItem] = {
            node_name_id_mapping.get(node["id"], node["id"]): RecalculationNodeItem(
                id=node_name_id_mapping.get(node["id"], node["id"]),
                size=node["size"],
                weight=node["weight"],
                targetId=node.get("targetId"),
            )
            for node in nodes
        }
        self._response_nodes = response_nodes

        response_edges: list[RecalculationEdgeItem] = []
        for edge in edges:
            response_edges.append(
                RecalculationEdgeItem(
                    id=node_edge_map.get(f'{[edge["sourceNodeId"], edge["targetNodeId"]]}', edge["id"]),
                    sourceNodeId=node_name_id_mapping[renamed_nodes.get(edge["sourceNodeId"], edge["sourceNodeId"])],
                    targetNodeId=node_name_id_mapping[renamed_nodes.get(edge["targetNodeId"], edge["targetNodeId"])],
                    size=edge["size"],
                    weight=edge["weight"],
                )
            )

        return RecalculationResult(
            nodes=response_nodes,
            edges=response_edges,
            nodesThresholds=self.nodes_thresholds,
            edgesThresholds=self.edges_thresholds,
            nodesThresholdsMinMax=self.nodelist.get_min_max(),
            edgesThresholdsMinMax=self.edgelist.get_min_max(),
        )

    def __get_nodelist_cols(self) -> list[str]:
        default_col = self.nodelist_default_col
        custom_cols = self.weight_cols
        return list([default_col]) + list(custom_cols)

    # TODO: WIP Layout experiments
    def _calc_layout(self, edgelist: pd.DataFrame, width: int, height: int) -> MutableMapping[str, Sequence[float]]:
        directed_graph = nx.DiGraph()
        source_col = edgelist.columns[0]
        target_col = edgelist.columns[1]
        weight_col = edgelist.columns[2]

        directed_graph.add_weighted_edges_from(edgelist.loc[:, [source_col, target_col, weight_col]].values)

        pos = nx.layout.spring_layout(
            directed_graph,
            k=self.spring_layout_config["k"],
            iterations=self.spring_layout_config["iterations"],
            threshold=self.spring_layout_config["nx_threshold"],
            seed=0,
        )

        all_x_coords: list[float] = []
        all_y_coords: list[float] = []

        for j in pos.values():
            all_x_coords.append(j[0])
            all_y_coords.append(j[1])

        min_x = min(all_x_coords)
        min_y = min(all_y_coords)
        max_x = max(all_x_coords)
        max_y = max(all_y_coords)

        return {
            i: [
                (j[0] - min_x) / (max_x - min_x) * (width - 150) + 75,
                (j[1] - min_y) / (max_y - min_y) * (height - 100) + 50,
            ]
            for i, j in pos.items()
        }

    def _prepare_nodes(
        self,
        nodelist: pd.DataFrame,
        mapped_node_targets: dict[NodeId, NodeTargetId] | None = None,
        nodes_custom_colors: NodesCustomColors | None = None,
    ) -> list[NodeItem]:
        node_names: set[str] = set(nodelist[self.event_col])
        nodes_custom_colors = nodes_custom_colors if nodes_custom_colors else {}

        cols = self.__get_nodelist_cols()
        nodes_set: list[NodeItem] = []

        for idx, node_name in enumerate(node_names):
            row = nodelist.loc[nodelist[self.event_col] == node_name]
            degree = {}
            weight = {}
            size = {}
            for weight_col in cols:
                max_degree = cast(float, nodelist[weight_col].max())
                r = row[weight_col]
                r = r.tolist()
                value = r[0]
                curr_degree = {
                    "degree": (abs(value)) / abs(max_degree) * 30 + 4,
                    "source": value,
                }
                degree[weight_col] = curr_degree
                size[weight_col] = curr_degree["degree"]
                weight[weight_col] = curr_degree["source"]

            nodelist_row_dict: dict = nodelist[nodelist[self.event_col] == node_name].iloc[0].to_dict()

            node = NodeItem(
                id=node_name,
                size=size,
                weight=weight,
                name=nodelist_row_dict[NAME_COL],
                isAggregated=nodelist_row_dict[IS_AGGREGATED_COL],
                isGroup=nodelist_row_dict[IS_GROUP_COL],
                children=nodelist.loc[nodelist[PARENT_ID_COL] == node_name, self.event_col].tolist(),
            )

            if mapped_node_targets is not None:
                target_node_id = mapped_node_targets.get(node_name)
                if target_node_id is not None:
                    node["targetId"] = target_node_id

            parent_node_id = nodelist_row_dict[PARENT_ID_COL]
            if parent_node_id is not None:
                node["parentNodeId"] = parent_node_id

            visibility_rule = None
            if nodelist_row_dict[IS_PINNED_COL]:
                visibility_rule = "pinned"
            elif nodelist_row_dict[IS_DISABLED_COL]:
                visibility_rule = "disabled"

            if visibility_rule is not None:
                node["visibilityRule"] = visibility_rule

            custom_color = nodes_custom_colors.get(node_name)
            if custom_color is not None:
                node["customColor"] = custom_color

            node_point = self.nodes_points.get(node_name)
            if node_point is not None:
                node["x"] = node_point["x"]
                node["y"] = node_point["y"]

            nodes_set.append(node)

        return nodes_set

    def _prepare_edges(
        self,
        edgelist: pd.DataFrame,
        nodes_items: list[NodeItem],
        edges_custom_colors: EdgesCustomColors | None = None,
    ) -> list[EdgeItem]:
        default_col = self.nodelist_default_col
        source_col = edgelist.columns[0]
        target_col = edgelist.columns[1]
        weight_col = edgelist.columns[2]
        custom_cols = self.weight_cols
        edges: list[EdgeItem] = []
        edges_custom_colors = edges_custom_colors if edges_custom_colors else {}

        edgelist["weight_norm"] = edgelist[weight_col] / edgelist[weight_col].abs().max()
        for _, row in edgelist.iterrows():
            default_col_weight: Weight = {
                "weight_norm": row.weight_norm,
                "weight": cast(float, row[weight_col]),
            }
            weights = {
                default_col: default_col_weight,
            }
            for custom_weight_col in custom_cols:
                weight = cast(float, row[custom_weight_col])
                max_weight = cast(float, edgelist[custom_weight_col].abs().max())
                weight_norm = weight / max_weight
                col_weight: Weight = {
                    "weight_norm": weight_norm,
                    "weight": weight,
                }
                weights[custom_weight_col] = col_weight

            source_node_name = str(row[source_col])
            target_node_name = str(row[target_col])

            custom_color = edges_custom_colors.get((source_node_name, target_node_name))

            # list comprehension faster than filter
            source_node = [node for node in nodes_items if node["id"] == source_node_name][0]
            target_node = [node for node in nodes_items if node["id"] == target_node_name][0]

            if source_node is not None and target_node is not None:  # type: ignore
                edge_item = EdgeItem(
                    id=generate(),
                    sourceNodeId=source_node_name,
                    targetNodeId=target_node_name,
                    weight={col_name: weight["weight"] for col_name, weight in weights.items()},
                    size={col_name: weight["weight_norm"] for col_name, weight in weights.items()},
                    aggregatedEdges=[],
                )

                if custom_color is not None:
                    edge_item["customColor"] = custom_color

                edges.append(edge_item)

        return edges

    @staticmethod
    def _to_json(data: Any) -> str:
        def convert_numpy(obj: Any) -> int:
            if isinstance(obj, np.integer):
                return int(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        return json.dumps(asdict(data), default=convert_numpy)

    @staticmethod
    def generate_id(size: int = 6, chars: str = string.ascii_uppercase + string.digits) -> str:
        return "el" + "".join(random.choice(chars) for _ in range(size))

    def save_to_file(self, path_to_graph_dump_file: str) -> None:
        with open(path_to_graph_dump_file, "w") as graph_dump_file:
            graph_dump_file.write(self._to_json(self.serialize_state()))

    def save_layout(self, path_to_layout_dump_file: str) -> None:
        with open(path_to_layout_dump_file, "w") as layout_dump_file:
            layout_dump_file.write(self._to_json(self.nodes_points))

    @staticmethod
    def __build_serialized_state_from_unknown_data(data: Any) -> SerializedState:
        tracker = Tracker(**data.pop("tracker"))
        settings = SerializedSettings(**data.pop("settings"))
        state_changes = StateChanges(**data.pop("stateChanges"))
        recalculation_changes = StateChanges(**data.pop("recalculationChanges"))

        return SerializedState(
            nodes=data["nodes"],
            edges=data["edges"],
            tracker=tracker,
            settings=settings,
            stateChanges=state_changes,
            recalculationChanges=recalculation_changes,
        )

    def __load_serialized_state_from_graph_dump(self, path_to_graph_dump_file: str) -> SerializedState | None:
        # noinspection PyBroadException
        try:
            with open(path_to_graph_dump_file, "r") as graph_dump_file:
                s = self.__build_serialized_state_from_unknown_data(json.load(graph_dump_file))
                return s

        except Exception:
            warnings.warn(f"Failed to load graph dump")
            return None

    @staticmethod
    def __load_nodes_points_from_layout_dump(path_to_layout_dump_file: str) -> NodesPoints:
        result: NodesPoints = {}

        # noinspection PyBroadException
        try:
            with open(path_to_layout_dump_file, "r") as layout_dump_file:
                raw_points = json.load(layout_dump_file)

                for node_id, raw_point in raw_points.items():
                    x = raw_point.get("x")
                    y = raw_point.get("y")
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        result[node_id] = NodePoint(x=x, y=y)
        except Exception:
            warnings.warn(f"Failed to load layout dump")

        return result

    def serialize_state(
        self,
    ) -> SerializedState:
        mapped_node_targets: dict[NodeId, NodeTargetId] = {
            node: target
            for target, nodes in self.targets.items()
            for node in (nodes if isinstance(nodes, list) else [nodes])
        }

        edgelist = self.edgelist.get_filtered_edges()
        nodelist = self.nodelist.nodelist_df.copy()

        source_col = edgelist.columns[0]
        target_col = edgelist.columns[1]

        # calc edge type
        # noinspection PyTypeChecker
        edgelist["type"] = edgelist.apply(
            lambda x: (
                mapped_node_targets.get(x[source_col])  # type: ignore
                if mapped_node_targets.get(x[source_col]) == "source"
                else mapped_node_targets.get(x[target_col]) or "suit"
            ),
            1,  # type: ignore
        )

        nodes_items = self._prepare_nodes(
            nodelist=nodelist,
            mapped_node_targets=mapped_node_targets,
            nodes_custom_colors=self.nodes_custom_colors,
        )

        edges_items = self._prepare_edges(
            edgelist=edgelist,
            nodes_items=nodes_items,
            edges_custom_colors=self.edges_custom_colors,
        )

        columns = [Column(id=col, name=col) for col in self.weight_cols]

        serialized_nodes_state = SerializedNodesState(
            normalizations=self._allowed_normalizations,
            selectedNormalizationId=self.nodes_norm_type if self.nodes_norm_type else "none",
            items=nodes_items,
            columns=columns,
            threshold=self.nodes_thresholds,
            weightsRange=self.nodes_weights_range,
            selectedWeightsColumnId=self.nodes_weight_col,
            targets=self._allowed_targets,
            sortField="name",  # TODO: Make it configurable
            sortOrder="asc",  # TODO: Make it configurable
        )

        serialized_edges_state = SerializedEdgesState(
            items=edges_items,
            normalizations=self._allowed_normalizations,
            selectedNormalizationId=self.edges_norm_type if self.edges_norm_type else "none",
            columns=columns,
            threshold=self.edges_thresholds,
            weightsRange=self.edges_weights_range,
            selectedWeightsColumnId=self.edges_weight_col,
        )

        # noinspection PyProtectedMember
        tracker = Tracker(
            hwid=RETE_CONFIG.user.pk,
            scope="transition_graph",
            eventstreamIndex=self.eventstream._eventstream_index,
        )

        settings = SerializedSettings(
            showEdgesWeightsOnCanvas=self.settings.show_weights,
            convertWeightsToPercents=self.settings.show_percents,
            showNodesNamesOnCanvas=self.settings.show_nodes_names,
            doNotFilterTargetNodes=self.settings.show_all_edges_for_targets,
            showNodesWithoutEdges=self.settings.show_nodes_without_links,
            showEdgesInfoOnHover=self.settings.show_edge_info_on_hover,
            openSidebarByDefault=self.settings.open_sidebar_by_default,
        )

        return SerializedState(
            tracker=tracker,
            restoreNodesPoints=all("x" in node and "y" in node for node in nodes_items),
            nodes=serialized_nodes_state,
            edges=serialized_edges_state,
            settings=settings,
            stateChanges=self._state_changes,
            recalculationChanges=self._recalculation_changes,
            # TODO: remove hardcode
            version="3.0.0",
        )

    @time_performance(
        scope="transition_graph",
        event_name="plot",
    )
    def plot(
        self,
        targets: TargetToNodesMap | None = None,
        edges_norm_type: NormType = None,
        nodes_threshold: ThresholdWithFallback | None = None,
        nodes_norm_type: NormType = None,
        edges_threshold: ThresholdWithFallback | None = None,
        nodes_weight_col: str | None = None,
        edges_weight_col: str | None = None,
        custom_weight_cols: list[str] | None = None,
        width: str | int | float | None = None,
        height: str | int | float | None = None,
        show_weights: bool | None = None,
        show_percents: bool | None = None,
        show_nodes_names: bool | None = None,
        show_all_edges_for_targets: bool | None = None,
        show_nodes_without_links: bool | None = None,
        show_edge_info_on_hover: bool | None = None,
        open_sidebar_by_default: bool | None = None,
        nodes_custom_colors: NodesCustomColors | None = None,
        edges_custom_colors: EdgesCustomColors | None = None,
        nodelist: Nodelist | pd.DataFrame | None = None,
        layout_dump: str | None = None,
        import_file: str | None = None,
    ) -> None:
        """
        Create interactive transition graph visualization with callback to sourcing eventstream.

        Parameters
        ----------
        edges_norm_type : {"full", "node", None}, default None
            Type of normalization that is used to calculate weights for graph edges.
            Based on ``edges_weight_col`` parameter the weight values are calculated.

            - If ``None``, normalization is not used, the absolute values are taken.
            - If ``full``, normalization across the whole eventstream.
            - If ``node``, normalization across each node (or outgoing transitions from each node).

            See :ref:`Transition graph user guide <transition_graph_weights>` for the details.

        nodes_norm_type : {"full", "node", None}, default None
            Currently not implemented. Always None.

        edges_weight_col : str, optional
            A column name from the :py:class:`.EventstreamSchema` which values will control the final
            edges' weights and displayed width as well.

            For each edge is calculated:

            - If ``None`` or ``user_id`` - the number of unique users.
            - If ``event_id`` - the number of transitions.
            - If ``session_id`` - the number of unique sessions.
            - If ``custom_col`` - the number of unique values in selected column.

            See :ref:`Transition graph user guide <transition_graph_weights>` for the details.

        edges_threshold : dict, optional
            Threshold mapping that defines the minimal weights for edges displayed on the canvas.

            - Keys should be of type str and contain the weight column names (the values from the
              :py:class:`.EventstreamSchema`).
            - Values of the dict are the thresholds for the edges that will be displayed.

            Support multiple weighting columns. In that case, logical OR will be applied.
            Edges with value less than at least one of thresholds will be hidden.
            Example: {'event_id': 100, user_id: 50}.

            See :ref:`Transition graph user guide<transition_graph_thresholds>` for the details.

        nodes_weight_col : str, optional
            A column name from the :py:class:`.EventstreamSchema` which values control the final
            nodes' weights and displayed diameter as well.

            For each node is calculated:

            - If ``None`` or ``user_id`` - the number of unique users.
            - If ``event_id`` - the number of events.
            - If ``session_id`` - the number of unique sessions.
            - If ``custom_col`` - the number of unique values in selected column.

            See :ref:`Transition graph user guide <transition_graph_weights>` for the details.

        nodes_threshold : dict, optional
            Threshold mapping that defines the minimal weights for nodes displayed on the canvas.

            - Keys should be of type str and contain the weight column names (the values from the
              :py:class:`.EventstreamSchema`).
            - Values of the dict are the thresholds for the nodes that will be displayed.
              They should be of type int or float.

            Support multiple weighting columns. In that case, logical OR will be applied.
            Nodes with value less than at least one of thresholds will be hidden.
            Example: {'event_id': 100, user_id: 50}.

            See :ref:`Transition graph user guide<transition_graph_thresholds>` for the details.

        custom_weight_cols : list of str, optional
            Custom columns from the :py:class:`.EventstreamSchema` that can be selected in ``edges_weight_col``
            and ``nodes_weight_col`` parameters. If ``session_col=session_id`` exists,
            it is added by default to this list.

        targets : dict, optional
            Events mapping that defines which nodes and edges should be colored for better visualization.

            - Possible keys: "positive" (green), "negative" (red), "source" (orange).
            - Possible values: list of events of a given type.

            See :ref:`Transition graph user guide<transition_graph_color_settings>` for the details.

        nodes_custom_colors : dict, optional
            Set nodes color explicitly. The dict keys are node names, the values are the corresponding colors.
            A color can be defined either as an HTML standard color name or a HEX code.
            See :ref:`Transition graph user guide<transition_graph_color_settings>` for the details.

        edges_custom_colors : dict, optional
            Set edges color explicitly. The dict keys are tuples of length 2, e.g. (path_start', 'catalog'),
            the values are the corresponding colors.
            A color can be defined either as an HTML standard color name or a HEX code.
            See :ref:`Transition graph user guide<transition_graph_color_settings>` for the details.

        width : str, int or float, default "100%"
            The width of the plot can be specified in the following ways:

            - In pixels (int or float);
            - In other CSS units (str). For example, the default value of "100%" means the plot will occupy 100%
              of the width of the Jupyter Notebook cell.

        height : str, int or float, default "60vh"
            The height of the plot can be specified as follows:

            - In pixels (int or float);
            - In other CSS units (str). For example, the default value of "60vh" means the plot will occupy 60%
              of the height of the browser window.

            The resulting height can't be lower than 600px.

        show_weights : bool, default True
            Hide/display the edge weight labels. By default, weights are shown.

        show_percents : bool, default False
            Display edge weights as percents. Available only if an edge normalization type is chosen.
            By default, weights are displayed in fractions.

        show_nodes_names : bool, default True
            Hide/display the node names. By default, names are shown.

        show_all_edges_for_targets : bool, default True
            This displaying option allows to ignore the threshold filters and always display
            any edge connected to a target node. By default, all such edges are shown.

        show_nodes_without_links : bool, default False
            Setting a threshold filter might remove all the edges connected to a node.
            Such isolated nodes might be considered as useless. This displaying option
            hides them in the canvas as well.

        show_edge_info_on_hover : bool, default True
            This parameter determines whether information about an edge (weight, source node, target node)
            is displayed when hovering the mouse over it.

        open_sidebar_by_default : bool, default True
            This parameter specifies whether the sidebar should be open by default when the interface is loaded.
            If set to True, the sidebar will be displayed upon initialization,
            providing users immediate access to its contents.
            If set to False, the sidebar will remain hidden until the user decides to open it.

        nodelist : pd.DataFrame, default None
            A DataFrame containing information about nodes, such as weights, parents, etc.

        layout_dump : str, default None
            A string path to a JSON file containing the configuration for nodes layout.

        import_file : str, default None
            A string path to a JSON file containing complete dump of a graph.

        Returns
        -------
            Rendered IFrame graph.

        Notes
        -----
        1. If all the edges connected to a node are hidden, the node becomes hidden as well.
           In order to avoid it - use ``show_nodes_without_links=True`` parameter in code or in the interface.
        2. The thresholds may use their own weighting columns both for nodes and for edges independently
           of weighting columns defined in ``edges_weight_col`` and ``nodes_weight_col`` arguments.

        See :doc:`TransitionGraph user guide </user_guides/transition_graph>` for the details.
        """
        if edges_norm_type is None and show_percents:
            raise ValueError("If show_percents=True, edges_norm_type should be 'full' or 'node'!")

        self.__prepare_state_for_plot(
            targets=targets,
            edges_norm_type=edges_norm_type,
            nodes_threshold=nodes_threshold,
            nodes_norm_type=nodes_norm_type,
            edges_threshold=edges_threshold,
            nodes_weight_col=nodes_weight_col,
            edges_weight_col=edges_weight_col,
            custom_weight_cols=custom_weight_cols,
            width=width,
            height=height,
            show_weights=show_weights,
            show_percents=show_percents,
            show_nodes_names=show_nodes_names,
            show_all_edges_for_targets=show_all_edges_for_targets,
            show_nodes_without_links=show_nodes_without_links,
            show_edge_info_on_hover=show_edge_info_on_hover,
            open_sidebar_by_default=open_sidebar_by_default,
            nodes_custom_colors=nodes_custom_colors,
            edges_custom_colors=edges_custom_colors,
            nodelist=nodelist,
            path_to_layout_dump_file=layout_dump,
            path_to_graph_dump_file=import_file,
        )

        widget_id = self.generate_id()

        serialized_state = self.serialize_state()

        display(
            HTML(
                self.render.show(
                    script_url=f"{self.graph_url}?id={widget_id}",
                    style=f"width: 100%; width: {self.width}; height: 60vh; height: {self.height}; min-height: 600px; box-sizing: border-box;",
                    state=self._to_json(serialized_state),
                    server=self.server,
                    bridge_model_id=self.bridge_id,
                    id=f"graph-{widget_id}",
                )
            )
        )

        # noinspection PyProtectedMember
        collect_data_performance(
            scope="transition_graph",
            event_name="metadata",
            called_params={
                "edges_norm_type": edges_norm_type,
                "nodes_norm_type": nodes_norm_type,
                "targets": targets,
                "nodes_threshold": nodes_threshold,
                "edges_threshold": edges_threshold,
                "nodes_weight_col": nodes_weight_col,
                "edges_weight_col": edges_weight_col,
                "custom_weight_cols": custom_weight_cols,
                "width": width,
                "height": height,
                "show_weights": show_weights,
                "show_percents": show_percents,
                "show_nodes_names": show_nodes_names,
                "show_all_edges_for_targets": show_all_edges_for_targets,
                "show_nodes_without_links": show_nodes_without_links,
                "show_edge_info_on_hover": show_edge_info_on_hover,
                "open_sidebar_by_default": open_sidebar_by_default,
            },
            not_hash_values=["edges_norm_type", "targets", "width", "height"],
            performance_data={
                "unique_nodes": len(serialized_state.nodes["items"]),
                "unique_links": len(serialized_state.edges["items"]),
            },
            eventstream_index=self.eventstream._eventstream_index,
        )

    def __prepare_state_for_plot(
        self,
        targets: TargetToNodesMap | None = None,
        edges_norm_type: NormType = None,
        nodes_threshold: ThresholdWithFallback | None = None,
        nodes_norm_type: NormType = None,
        edges_threshold: ThresholdWithFallback | None = None,
        nodes_weight_col: str | None = None,
        edges_weight_col: str | None = None,
        custom_weight_cols: list[str] | None = None,
        width: str | int | float | None = None,
        height: str | int | float | None = None,
        show_weights: bool | None = None,
        show_percents: bool | None = None,
        show_nodes_names: bool | None = None,
        show_all_edges_for_targets: bool | None = None,
        show_nodes_without_links: bool | None = None,
        show_edge_info_on_hover: bool | None = None,
        open_sidebar_by_default: bool | None = None,
        nodes_custom_colors: NodesCustomColors | None = None,
        edges_custom_colors: EdgesCustomColors | None = None,
        nodelist: Nodelist | pd.DataFrame | None = None,
        path_to_layout_dump_file: str | None = None,
        path_to_graph_dump_file: str | None = None,
    ) -> None:
        serialized_state_from_file = (
            self.__load_serialized_state_from_graph_dump(path_to_graph_dump_file) if path_to_graph_dump_file else None
        )

        if path_to_layout_dump_file:
            self.nodes_points = self.__load_nodes_points_from_layout_dump(path_to_layout_dump_file)
        elif serialized_state_from_file:
            self.nodes_points = self._extract_nodes_points_from_serialized_state(serialized_state_from_file)

        if serialized_state_from_file:
            self._state_changes = serialized_state_from_file.stateChanges
            self._recalculation_changes = serialized_state_from_file.recalculationChanges

        if show_weights is not None:
            self.settings.show_weights = show_weights
        elif serialized_state_from_file:
            self.settings.show_weights = serialized_state_from_file.settings.showEdgesWeightsOnCanvas

        if show_percents is not None:
            self.settings.show_percents = show_percents
        elif serialized_state_from_file:
            self.settings.show_percents = serialized_state_from_file.settings.convertWeightsToPercents

        if show_nodes_names is not None:
            self.settings.show_nodes_names = show_nodes_names
        elif serialized_state_from_file:
            self.settings.show_nodes_names = serialized_state_from_file.settings.showNodesNamesOnCanvas

        if show_all_edges_for_targets is not None:
            self.settings.show_all_edges_for_targets = show_all_edges_for_targets
        elif serialized_state_from_file:
            self.settings.show_all_edges_for_targets = serialized_state_from_file.settings.doNotFilterTargetNodes

        if show_nodes_without_links is not None:
            self.settings.show_nodes_without_links = show_nodes_without_links
        elif serialized_state_from_file:
            self.settings.show_nodes_without_links = serialized_state_from_file.settings.showNodesWithoutEdges

        if show_edge_info_on_hover is not None:
            self.settings.show_edge_info_on_hover = show_edge_info_on_hover
        elif serialized_state_from_file:
            self.settings.show_edge_info_on_hover = serialized_state_from_file.settings.showEdgesInfoOnHover

        if open_sidebar_by_default is not None:
            self.settings.open_sidebar_by_default = open_sidebar_by_default
        elif serialized_state_from_file:
            self.settings.open_sidebar_by_default = serialized_state_from_file.settings.openSidebarByDefault

        self.targets = {}
        if targets:
            self.targets = targets
        elif serialized_state_from_file:
            targets_result: TargetToNodesMap = {}
            for node in serialized_state_from_file.nodes["items"]:
                target_id = node.get("targetId")
                if target_id:
                    if target_id not in targets_result:
                        targets_result[target_id] = []
                    targets_result[target_id].append(node["id"])  # type: ignore
            self.targets = targets_result

        self.nodes_norm_type = None
        if nodes_norm_type:
            self.nodes_norm_type = nodes_norm_type
        elif serialized_state_from_file:
            serialized_nodes_norm_type = serialized_state_from_file.nodes["selectedNormalizationId"]
            if serialized_nodes_norm_type != "none":
                self.nodes_norm_type = serialized_nodes_norm_type

        self.edges_norm_type = None
        if edges_norm_type:
            self.edges_norm_type = edges_norm_type
        elif serialized_state_from_file:
            serialized_edges_norm_type = serialized_state_from_file.edges["selectedNormalizationId"]
            if serialized_edges_norm_type != "none":
                self.edges_norm_type = serialized_edges_norm_type

        self.nodelist_default_col = self.eventstream.schema.event_id
        self.edgelist_default_col = self.eventstream.schema.event_id

        self.weight_cols = self._define_weight_cols(custom_weight_cols)

        if nodes_weight_col:
            self.nodes_weight_col = nodes_weight_col
        elif serialized_state_from_file:
            self.nodes_weight_col = serialized_state_from_file.nodes["selectedWeightsColumnId"]
        else:
            self.nodes_weight_col = self.eventstream.schema.user_id

        if edges_weight_col:
            self.edges_weight_col = edges_weight_col
        elif serialized_state_from_file:
            self.edges_weight_col = serialized_state_from_file.edges["selectedWeightsColumnId"]
        else:
            self.edges_weight_col = self.eventstream.schema.user_id

        if width is not None:
            self.width = f"{width}px" if isinstance(width, (int, float)) else width

        if height is not None:
            self.height = f"{height}px" if isinstance(height, (int, float)) else height

        self.nodes_custom_colors = {}
        if nodes_custom_colors:
            self.nodes_custom_colors = nodes_custom_colors
        elif serialized_state_from_file:
            nodes_custom_colors_result: NodesCustomColors = {}
            for node in serialized_state_from_file.nodes["items"]:
                custom_color = node.get("customColor")
                if custom_color:
                    nodes_custom_colors_result[node["id"]] = custom_color
            self.nodes_custom_colors = nodes_custom_colors_result

        self.edges_custom_colors = {}
        if edges_custom_colors:
            self.edges_custom_colors = edges_custom_colors
        elif serialized_state_from_file:
            edges_custom_colors_result: EdgesCustomColors = {}
            for edge in serialized_state_from_file.edges["items"]:
                custom_color = edge.get("customColor")
                if custom_color:
                    edges_custom_colors_result[(edge["sourceNodeId"], edge["targetNodeId"])] = custom_color
            self.edges_custom_colors = edges_custom_colors_result

        # calculate nodelist & edgelist on initial eventstream without any thresholds
        self.initial_nodelist: Nodelist = Nodelist(
            weight_cols=self.weight_cols,
            time_col=self.event_time_col,
            event_col=self.event_col,
        )
        self.initial_nodelist.calculate_nodelist(data=self.eventstream.to_dataframe())

        self.initial_edgelist: Edgelist = Edgelist(eventstream=self.eventstream)
        self.initial_edgelist.calculate_edgelist(
            weight_cols=self.weight_cols,
            norm_type=self.edges_norm_type,
        )

        self.nodes_weights_range = self.initial_nodelist.get_min_max()
        self.edges_weights_range = self.initial_edgelist.get_min_max()

        self.nodes_thresholds = {}
        if nodes_threshold:
            self.nodes_thresholds = self.__threshold_fallback(nodes_threshold, threshold_type="nodes")
        elif serialized_state_from_file:
            self.nodes_thresholds = serialized_state_from_file.nodes.get("threshold", {})

        self.edges_thresholds = {}
        if edges_threshold:
            self.edges_thresholds = self.__threshold_fallback(edges_threshold, threshold_type="edges")
        elif serialized_state_from_file:
            self.edges_thresholds = serialized_state_from_file.edges.get("threshold", {})

        external_nodelist_df: pd.DataFrame | None = None
        if nodelist:
            external_nodelist_df = nodelist if isinstance(nodelist, pd.DataFrame) else nodelist.nodelist_df
        elif serialized_state_from_file:
            external_nodelist_df = pd.DataFrame(self.make_nodelist_from_serialized_state(serialized_state_from_file))
        self.__apply_nodelist(nodelist_df=external_nodelist_df)

    def __apply_nodelist(self, nodelist_df: pd.DataFrame | None = None) -> EventstreamType:
        prev_nodes_min_max = (
            self.nodelist.get_min_max()
            if hasattr(self, "nodelist") and self.nodelist is not None  # type: ignore
            else None
        )

        prev_edges_min_max = (
            self.edgelist.get_min_max()
            if hasattr(self, "edgelist") and self.edgelist is not None  # type: ignore
            else None
        )

        self.nodelist: Nodelist = self.initial_nodelist.copy()
        if nodelist_df is not None:
            self.nodelist.update(nodelist_df)

        curr_stream = self.eventstream

        disabled_nodes = self.nodelist.get_disabled_nodes()
        if len(disabled_nodes) > 0:
            curr_stream = curr_stream.filter_events(
                func=lambda df, schema: ~df[schema.event_name].isin(disabled_nodes)  # type: ignore
            )

        rename_rules = self.nodelist.groups_to_rename_rules()
        if len(rename_rules) > 0:
            curr_stream = curr_stream.rename(rules=rename_rules)  # type: ignore

        self.nodelist.calculate_nodelist(data=curr_stream.to_dataframe())

        if prev_nodes_min_max is not None:
            self.nodes_thresholds = self.nodelist.fit_threshold(
                threshold=self.nodes_thresholds, prev_min_max=prev_nodes_min_max
            )

        self.nodelist.update_threshold(nodes_thresholds=self.nodes_thresholds)

        out_of_threshold_nodes = self.nodelist.get_out_of_threshold_nodes(only_ungrouped=True)
        if len(out_of_threshold_nodes) > 0:
            curr_stream = curr_stream.filter_events(  # type: ignore
                func=lambda df, schema: ~df[schema.event_name].isin(out_of_threshold_nodes)
            )

        self.edgelist: Edgelist = Edgelist(eventstream=curr_stream)
        self.edgelist.calculate_edgelist(
            weight_cols=self.weight_cols,
            norm_type=self.edges_norm_type,
        )

        if prev_edges_min_max is not None:
            self.edges_thresholds = self.edgelist.fit_threshold(
                threshold=self.edges_thresholds, prev_min_max=prev_edges_min_max
            )

        self.edgelist.update_threshold(edges_threshold=self.edges_thresholds)

        # use aliases after all calculations
        aliases_rename_rules = self.nodelist.renamed_events_to_rename_rules()
        if len(aliases_rename_rules) > 0:
            curr_stream = curr_stream.rename(rules=aliases_rename_rules)  # type: ignore

        return curr_stream

    def __threshold_fallback(
        self, threshold: ThresholdWithFallback, threshold_type: Literal["nodes"] | Literal["edges"]
    ) -> ThresholdValueMap:
        result: ThresholdValueMap = {}

        for key, value in threshold.items():
            weights_range = (
                self.nodes_weights_range.get(key, None)
                if threshold_type == "nodes"
                else self.edges_weights_range.get(key, None)
            )

            if weights_range is None:
                raise ValueError(f"threshold is invalid. Column '{key}' doesn't found!")

            if isinstance(value, dict):
                result[key] = value
                continue

            result[key] = {"min": float(value), "max": float(weights_range["max"])}

        return result
