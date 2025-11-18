from __future__ import annotations

import json
from typing import Hashable, Tuple

import numpy as np
import pandas as pd

EVENTSTREAM_KEYS = ["shape", "custom_cols", "unique_users", "unique_events", "hash", "eventstream_hist", "index"]


def to_json(data: str) -> dict | float:
    try:
        return json.loads(data)
    except:
        return np.nan


def get_eventstream_before(data: pd.Series) -> dict:
    arg_dict = data["params"]
    eventstream_args: dict = data["eventstream_args"]
    if all([pd.isna(t) for t in eventstream_args.values()]):
        eventstream_args = {}

    if len(arg_dict) == 0:
        return eventstream_args

    data = arg_dict[0].get("performance_info", {})
    data_processor_output: dict

    data_processor_output = data.get("parent", {})  # type:ignore
    default_output = {}
    if all(key in data.keys() for key in EVENTSTREAM_KEYS):
        default_output = {k: v for k, v in data.items() if k in EVENTSTREAM_KEYS}

    result = {**eventstream_args, **(data_processor_output or default_output)}
    return result


def get_eventstream_after(arg_dict: list[dict]) -> dict:
    if len(arg_dict) == 0:
        return {}

    data_processor_output = arg_dict[0].get("performance_info", {}).get("child", {})
    default_output = {}
    if len(arg_dict) > 1 and all(key in arg_dict[1].keys() for key in EVENTSTREAM_KEYS):
        default_output = {k: v for k, v in arg_dict[1].items() if k in EVENTSTREAM_KEYS}

    return data_processor_output or default_output


def get_out_attrs(arg_dict: list[dict]) -> dict:
    first, last = {}, {}
    if len(arg_dict) > 0:
        first = arg_dict[0].get("performance_info", {})
        first.pop("child", None)
        first.pop("parent", None)

        if all(key in first.keys() for key in EVENTSTREAM_KEYS):
            first = {k: v for k, v in first.items() if k not in EVENTSTREAM_KEYS}

    if len(arg_dict) > 1:
        last = arg_dict[1].get("performance_info", {})
        last.pop("child", None)
        last.pop("parent", None)

        if all(key in last.keys() for key in EVENTSTREAM_KEYS):
            last = {k: v for k, v in first.items() if k not in EVENTSTREAM_KEYS}

    return last or first


def set_parent(df: pd.DataFrame, index_col: str = "index", parent_col: str = "parent_index") -> pd.Series:
    """Parses the data as a sequence of brackets and sets the index
    of the parent bracket for all internal data. The algorithm works
    backwards to process the broken sequences.
    """
    df = df.sort_values(by=index_col)
    position = df.shape[0] - 1

    parent_stack, event_stack, parents = [0], [], []
    while position >= 0:
        if parent_stack[-1] == 0 and not (
            df.iloc[position]["event_custom_name"].endswith("_end")
            or df.iloc[position]["event_custom_name"].endswith("_tracker")
        ):
            parents.append(-1)
        else:
            parents.append(parent_stack[-1])
        full_name = f"{df.iloc[position]['scope']}_{df.iloc[position]['event_name']}"
        if df.iloc[position]["event_custom_name"].endswith("_end"):
            event_stack.append(full_name)
            parent_stack.append(df.iloc[position][index_col])
        if df.iloc[position]["event_custom_name"].endswith("_start"):
            while full_name in event_stack:
                parent_stack.pop()
                if event_stack.pop() == full_name:
                    break

        position -= 1

    return pd.Series(parents[::-1], index=df.index, name=parent_col)


def prepare_data(
    df: pd.DataFrame,
    index_col: str = "index",
    parent_col: str = "parent_index",
    full_index: str = "full_index",
    full_parent_index: str = "full_parent_index",
    event_full_name: str = "event_full_name",
    buffer_index_name: str = "_default_index",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Collapses each bracket group into a single event and
    writes the latest metadata for the current group. The broken sequences are
    excluded from consideration. Returns two dataframes: processed and broken data.
    """
    if df.empty:
        raise ValueError("The data is empty")

    df.sort_values(index_col, inplace=True)
    df[parent_col] = pd.concat([set_parent(group) for name, group in df.groupby(["user_id", "jupyter_kernel_id"])])
    broken = df[df[parent_col] == -1]
    df = df[df.parent_index != -1].copy()
    df[full_index] = df[index_col].apply(str) + df["user_id"] + df["jupyter_kernel_id"]
    df[full_parent_index] = df[parent_col].apply(str) + df["user_id"] + df["jupyter_kernel_id"]
    df[event_full_name] = df["scope"] + "_" + df["event_name"]

    meta_cols = ["eventstream_index", "parent_eventstream_index", "child_eventstream_index", "params"]

    meta = (
        df[(df["event_name"] == "metadata")]
        .groupby(full_parent_index)
        .agg({col: list if col == "params" else "last" for col in meta_cols})
    )
    df.reset_index(inplace=True, names=[buffer_index_name])
    df.set_index(full_index, inplace=True)

    df["params"] = [[] for _ in range(df.shape[0])]
    df.loc[meta.index, meta_cols] = meta[meta_cols]
    df.reset_index(inplace=True)
    df.set_index(buffer_index_name, inplace=True)
    df.index.name = None

    df["session_ix"] = pd.concat([set_sessions(group) for name, group in df.groupby(["user_id"])])

    return df.loc[(df.event_name != "metadata") & ~df.event_custom_name.str.endswith("_start")], broken


def uncover_params(df: pd.DataFrame) -> pd.DataFrame:
    df["args"] = df.params.apply(lambda l: l[0].get("args", {}) if len(l) > 0 else {})
    df["eventstream_args"] = df[["child_eventstream_index", "eventstream_index", "parent_eventstream_index"]].to_dict(
        "records"
    )

    df["eventstream_input"] = df[["eventstream_args", "params"]].apply(get_eventstream_before, axis=1)
    df["eventstream_output"] = df.params.apply(get_eventstream_after)
    df["output_attributes"] = df.params.apply(get_out_attrs)

    return df


def set_sessions(df: pd.DataFrame) -> pd.Series:
    df["is_root_call"] = df["parent_index"] == 0
    df["session_ix"] = df.loc[::-1, "is_root_call"].cumsum()[::-1]
    return df.loc[:, "session_ix"]


def get_inner_calls(
    data: pd.DataFrame, parent_index: Hashable, index_col: str = "full_index", parent_col: str = "full_parent_index"
) -> pd.DataFrame:
    parent_ids = [parent_index]
    inner_ids = []
    while parent_ids:
        current_parent = parent_ids.pop()
        inner_calls = data[data[parent_col] == current_parent]
        parent_ids.extend(inner_calls[index_col])
        inner_ids.append(current_parent)
    return data[data[index_col].isin(inner_ids)]


def aggregate_to_top_calls(df: pd.DataFrame, front_df: pd.DataFrame) -> pd.DataFrame:
    result = df[(df["parent_index"] == 0)].copy()
    cols_to_calc = ["args", "eventstream_input", "eventstream_output", "output_attributes"]

    result.drop(columns=cols_to_calc, inplace=True)
    for col in cols_to_calc:
        grouped = df[df[col] != {}].groupby(["user_id", "session_ix"])[col].last()
        result = result.join(grouped, on=["user_id", "session_ix"])

    timestamp_df = (
        df.groupby(["user_id", "session_ix"])["event_timestamp_ms"]
        .agg(["first", "last"])
        .rename(columns={"first": "timestamp_start", "last": "timestamp_end"})
    )
    result = result.join(timestamp_df, on=["user_id", "session_ix"])

    front_df["timestamp_start"] = front_df["event_timestamp_ms"]
    front_df["timestamp_end"] = front_df["event_timestamp_ms"]
    result = pd.concat([result, front_df]).sort_values("index")

    return result


def process_data(data: pd.DataFrame, only_calls: bool = True) -> pd.DataFrame:
    """Processes raw data from the database."""
    df = data.copy()
    back_df, front_df = separate_data_sources(df)
    back_df["params"] = back_df["params"].apply(to_json)
    back_df = prepare_data(back_df)[0]
    back_df = uncover_params(back_df)

    if only_calls:
        df = aggregate_to_top_calls(back_df, front_df)

    else:
        df = pd.concat([back_df, front_df]).sort_values("index")

    return df


def separate_data_sources(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    mask = df["browser"] == "Python Requests"
    back_df = df.loc[mask].copy()
    front_df = df.loc[~mask].copy()

    return back_df, front_df
