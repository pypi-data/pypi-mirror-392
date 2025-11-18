from __future__ import annotations

import pandas as pd

from retentioneering.backend.tracker import collect_data_performance, time_performance
from retentioneering.data_processor import DataProcessor
from retentioneering.eventstream.segments import _get_segment_mask
from retentioneering.eventstream.types import EventstreamSchemaType, EventstreamType
from retentioneering.params_model import ParamsModel
from retentioneering.utils.doc_substitution import docstrings
from retentioneering.utils.hash_object import hash_dataframe


class DropSegmentParams(ParamsModel):
    name: str


@docstrings.get_sections(base="DropSegment")  # type: ignore
class DropSegment(DataProcessor):
    """
    Remove segment synthetic events from eventstream.

    Parameters
    ----------
    name : str
        Segment name to remove.

    Returns
    -------
    EventstreamType
        Eventstream with removed segment.
    """

    params: DropSegmentParams

    @time_performance(scope="drop_segment", event_name="init")
    def __init__(self, params: DropSegmentParams) -> None:
        super().__init__(params=params)

    @time_performance(scope="drop_segment", event_name="apply")
    def apply(self, df: pd.DataFrame, schema: EventstreamSchemaType) -> pd.DataFrame:
        hash_before = hash_dataframe(df)
        shape_before = df.shape
        mask = _get_segment_mask(df, schema, self.params.name)

        df.drop(df[mask].index, inplace=True)

        collect_data_performance(
            scope="drop_segment",
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
