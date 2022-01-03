"""
UTILITY FUNCTIONS

load_data: Load dataframe from filepath
list_remove_duplicates: drop duplicate elements from list
list_flatten: flatten nested list
n_batch: generator for n-sized list batches
list_batch: get n-sized chunks from n_batch generator
df_to_csv: write csv either create new or append to existing
timestamp_now: get string
sleep_countdown(): countdown in console

"""

import os
import sys
import time
import pandas as pd
from datetime import datetime
import streamlit as st
from functools import wraps
import logging

# ----------------------------------------
# -- Plot data
# ----------------------------------------


@st.cache(allow_output_mutation=True)
def load_data(filepath, parse_dates=False):
    """Load data from filepath. parse_dates takes list of date columns to convert to datetime"""
    return pd.read_csv(filepath, parse_dates=parse_dates)


def group_search_interest_on_time_unit(df, unit="M"):
    """Returns aggregated dataframe specified time unit. Uses pandas grouper
    see frequency options for other time units like weekly or annually"""

    # assert date as index for pd.Grouper
    assert (
        df.index.dtype == "datetime64[ns]"
    ), "Dataframe misses date index. No grouping on date unit possible."
    # assert keyword column
    assert (
        "keyword" in df.columns
    ), "Dataframe misses keyword column. No grouping on date unit possible."

    # groups to unit averages (defaults to monthly)
    df = df.groupby(["keyword", pd.Grouper(freq=unit)]).mean().reset_index()

    return df


# ----------------------------------------
# -- General-purpose utilities
# ----------------------------------------


def list_remove_duplicates(the_list):
    """Removes duplicates from list elements whilst preserving element order

    Args:
        list with string elements

    Returns:
        Sorted list without duplicates

    """
    seen = set()
    seen_add = seen.add
    return [x for x in the_list if not (x in seen or seen_add(x))]


def list_flatten(nested_list):
    """Flattens nested list"""
    return [element for sublist in nested_list for element in sublist]


def n_batch(lst, n=5):
    """Yield successive n-sized chunks from list lst

    Args:
        lst (list): list object
        n (int): batch size to divide list

    Returns:
        List: nested list, divided lst into batches of len(lst)/n lists
    """

    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def list_batch(lst, n=5):
    """ "Divides a list into a list of lists with n-sized length"""
    return list(n_batch(lst=lst, n=n))


def df_to_csv(df, filepath):
    """Export df to CSV. If it exists already, append data."""
    # file does not exist --> write header
    if not os.path.isfile(f"{filepath}"):
        df.to_csv(f"{filepath}", index=False)
    # file exists --> append data without header
    else:
        df.to_csv(f"{filepath}", index=False, header=False, mode="a")


def timestamp_now():
    """Return UTC timestamp string in format: yyyy/mm/dd-hh/mm/ss"""
    return datetime.utcnow().strftime("%y%m%d-%H%M%S")


def sleep_countdown(duration, print_step=2):
    """Sleep for certain duration and print remaining time in steps of print_step

    Args:
        duration (int): duration of timeout
        print_step (int): steps to print countdown

    Returns
        None: Countdown in console
    """
    for i in range(duration, 0, -print_step):
        time.sleep(print_step)
        sys.stdout.write(str(i - print_step) + " ")
        sys.stdout.flush()


def wrap_logging_transform_df(func):
    """Wrapper to compare df before and after transformation"""

    @wraps(func)
    def with_logging(*args, **kwargs):

        try:
            df_orig: pd.DataFrame = args[0]
            df_edit: pd.DataFrame = func(*args, **kwargs)

            # df_edit and df_orig should be dataframe
            if not isinstance(df_orig, pd.DataFrame):
                raise TypeError(
                    f"{func.__name__} args[0] is not a dataframe, but type: {type(args[0])}). Skip logging."
                )

            if not isinstance(df_edit, pd.DataFrame):
                raise TypeError(
                    f"{func.__name__} did not return dataframe, but type: {type(df_edit)}. Skip logging."
                )

            else:
                logging_transform_df(df_orig, df_edit, func.__name__)
                return df_edit

        except Exception as e:
            logging.error(f"{func.__name__} - wrap_logging_transform_df(): {e}")

        return func(*args, **kwargs)

    return with_logging


def logging_transform_df(
    df_orig: pd.DataFrame, df_edit: pd.DataFrame, step_name: str = "compare df"
) -> None:
    "Logging utility to show row difference between two dataframes"
    N_orig, N_edit = len(df_orig), len(df_edit)
    N_diff = N_orig - N_edit
    pct_diff = N_diff / N_orig * 100

    # sign for added or removed rows
    if N_diff > 0:
        sign = "-"
    if N_diff < 0:
        N_diff *= -1
        pct_diff *= -1
        sign = "+"
    if N_diff == 0:
        sign = ""

    logging.info(
        f"{step_name} --> {sign}{N_diff} records ({sign}{pct_diff:.2f}%, {N_orig}-{N_edit})"
    )


@wrap_logging_transform_df
def drop_missings_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    "Return df without missings and duplicates"
    df_nomiss = df.dropna()
    df_nodup = df_nomiss.drop_duplicates()

    return df_nodup.reset_index(drop=True)


def get_raw_data(filepath) -> pd.DataFrame:
    "Return data without preprocessing"
    logging.info(f"Reading file: {filepath}")
    return pd.read_csv(filepath, parse_dates=["date"])
