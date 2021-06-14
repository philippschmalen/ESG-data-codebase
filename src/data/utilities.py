"""
UTILITY FUNCTIONS

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
from datetime import datetime


def list_remove_duplicates(l):
    """Removes duplicates from list elements whilst preserving element order

    Args:
        list with string elements

    Returns:
        Sorted list without duplicates

    """
    seen = set()
    seen_add = seen.add
    return [x for x in l if not (x in seen or seen_add(x))]


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
    """"Divides a list into a list of lists with n-sized length"""
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
