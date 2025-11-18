from __future__ import annotations

import numpy as np
import pandas as pd

from retentioneering.backend.tracker import collect_data_performance, time_performance
from retentioneering.data_processor import DataProcessor
from retentioneering.eventstream.segments import (
    SEGMENT_DELIMITER,
    SEGMENT_TYPE,
    _create_segment_event,
    _extract_segment_values,
    _get_segment_mask,
)
from retentioneering.eventstream.types import (
    AddSegmentType,
    EventstreamSchemaType,
    EventstreamType,
)
from retentioneering.params_model import ParamsModel
from retentioneering.utils.doc_substitution import docstrings
from retentioneering.utils.hash_object import hash_dataframe
from retentioneering.widget.widgets import ListOfString, ReteFunction


class RenameSegmentParams(ParamsModel):
    old_name: str
    new_name: str


@docstrings.get_sections(base="RenameSegment")  # type: ignore
class RenameSegment(DataProcessor):
    """
    Rename segment for synthetic eventstream events.

    Parameters
    ----------
    old_name : str
        Old segment name to change.
    new_name : str
        New segment name to set.

    Returns
    -------
    EventstreamType
        Eventstream with renamed segment.
    """

    params: RenameSegmentParams

    @time_performance(scope="rename_segment", event_name="init")
    def __init__(self, params: RenameSegmentParams) -> None:
        super().__init__(params=params)

    @time_performance(scope="rename_segment", event_name="apply")
    def apply(self, df: pd.DataFrame, schema: EventstreamSchemaType) -> pd.DataFrame:
        old_name = self.params.old_name
        new_name = self.params.new_name
        hash_before = hash_dataframe(df)
        shape_before = df.shape

        mask = _get_segment_mask(df, schema, old_name)
        df.loc[mask, schema.event_name] = df.loc[mask, schema.event_name].apply(lambda x: x.replace(old_name, new_name))

        collect_data_performance(
            scope="rename_segment",
            event_name="metadata",
            called_params=self.to_dict()["values"],
            performance_data={
                "parent": {
                    "shape": shape_before,
                    "hash": hash_before,
                },
                "child": {
                    "shape": df.shape,
                    "hash": hash_dataframe(df),
                },
            },
        )
        return df
