from __future__ import annotations

import json
import os
import uuid
import warnings
from dataclasses import asdict, field
from pathlib import Path
from typing import Optional, Type, Union

from pydantic import BaseConfig
from pydantic.dataclasses import dataclass

from retentioneering.utils.hwid import get_hwid  # type: ignore


@dataclass
class TrackingConfig(BaseConfig):
    """
    Configuration for tracking.
    """

    is_tracking_allowed: bool = True


@dataclass
class UserConfig(BaseConfig):
    pk: str = ""

    def __post_init__(self) -> None:
        if self.pk == "":
            self.pk = str(uuid.uuid4())


@dataclass
class TransitionGraphConfig(BaseConfig):
    """
    Configuration for the transition graph.
    """

    width: Union[float, int, str] = "100%"
    height: Union[float, int, str] = "800px"
    show_weights: bool = True
    show_percents: bool = False
    show_nodes_names: bool = True
    show_all_edges_for_targets: bool = True
    show_nodes_without_links: bool = False
    show_edge_info_on_hover: bool = True
    open_sidebar_by_default: bool = True


@dataclass
class PreprocessingGraphConfig(BaseConfig):
    """
    Configuration for the preprocessing graph.
    """

    width: int = 960
    height: int = 600


DEFAULT_CONFIG = {
    "user": asdict(UserConfig()),
    "transition_graph": asdict(TransitionGraphConfig()),
    "preprocessing_graph": asdict(PreprocessingGraphConfig()),
}


@dataclass
class Config(BaseConfig):
    """
    Configuration for the application.
    """

    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    user: UserConfig = field(default_factory=UserConfig)
    transition_graph: TransitionGraphConfig = field(default_factory=TransitionGraphConfig)
    preprocessing_graph: PreprocessingGraphConfig = field(default_factory=PreprocessingGraphConfig)

    def _inner_mapping(self, _validate: bool = True) -> dict[str, Type[BaseConfig]]:
        # !!! DO NOT SET _validate to False except for tests !!!
        # self.__annotations__ has type dict[str, str], and it will be simpler than obtain class by name from globals or something like that
        # And it's method because of pydantic dataclasses
        mapping = {
            "tracking": TrackingConfig,
            "user": UserConfig,
            "transition_graph": TransitionGraphConfig,
            "preprocessing_graph": PreprocessingGraphConfig,
        }

        if _validate and (missing_keys := set(self.__annotations__.keys()) - set(mapping.keys())):
            raise ValueError(f"The keys of __annotations__ and inner mapping are not the same. Lost {missing_keys}")
        return mapping  # type: ignore

    @staticmethod
    def _get_path_for_config() -> Optional[str]:
        config_filename = ".retentioneering_config.json"
        home = str(Path.home())
        if os.access(f"{home}", os.W_OK):
            return f"{home}/{config_filename}"
        elif os.access(".", os.W_OK):
            return config_filename
        else:
            return None

    def __post_init__(self) -> None:
        config_path = self._get_path_for_config()
        if config_path is None:
            return None
        # check if file exists
        if not os.path.isfile(config_path):
            with open(config_path, "w") as f:
                json.dump(DEFAULT_CONFIG, f)
        self.load()

    def load(self) -> None:
        config_path = self._get_path_for_config()
        if config_path is None:
            return None
        with open(config_path, "r") as f:
            try:
                config: dict[str, dict] = json.load(f)
                mapping = self._inner_mapping()
                for section, _class in mapping.items():
                    section_data = config.get(section, {})
                    setattr(self, section, _class(**section_data))  # type: ignore

            except json.decoder.JSONDecodeError:
                warnings.warn("Invalid config file. Please fix it and try again. Current config file is default.")

            else:
                # update config file from actual state
                current_config_data = asdict(self)
                if config.get("tracking", None) is None:
                    del current_config_data["tracking"]

                with open(config_path, "w") as f:
                    json.dump(current_config_data, f)

    def save(self) -> None:
        config_path = self._get_path_for_config()
        if config_path is None:
            return None

        self._write_current_config(config_path)

    def _write_current_config(self, config_path: str) -> None:
        sections = self._inner_mapping().keys()
        config_data = {section: asdict(getattr(self, section)) for section in sections}
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)


RETE_CONFIG = Config()
