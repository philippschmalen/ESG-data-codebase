"""
Extract data from Google trends with the pytrends package
Methods take one keyword, call pytrends and return processed data as CSV or dataframe

There are two main functions:
    * get_related_queries_pipeline: Returns dataframe of trending searches for a given topic
    * get_interest_over_time: Returns CSV with interest over time for specified keywords

"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from random import randint
from pytrends.request import TrendReq

from utilities import list_batch, df_to_csv, sleep_countdown

logger = logging.getLogger(__name__)


def create_pytrends_session():
    """Create pytrends TrendReq() session on which .build_payload() can be called """
    pytrends_session = TrendReq()

    return pytrends_session


# ----------------------------------------------------------
# Google trends: related queries
# ----------------------------------------------------------


def get_related_queries(pytrends_session, keyword_list, cat=0, geo=""):
    """Returns a dictionary with a dataframe for each keyword
    Calls pytrend's related_queries()

    Args:
        pytrends_session (object): TrendReq() session of pytrend
        keyword_list (list): Used as input for query and passed to TrendReq().build_payload()
        cat (int): see https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories
        geo (str): Geolocation like US, UK

    Returns:
        Dictionary: Dict with dataframes with related query results
    """
    assert isinstance(
        keyword_list, list
    ), f"keyword_list should be string. Instead of type {type(keyword_list)}"

    df_related_queries = pd.DataFrame()

    try:
        pytrends_session.build_payload(keyword_list, cat=cat, geo=geo)
        df_related_queries = pytrends_session.related_queries()
        logging.info(f"Query succeeded for {*keyword_list ,}")

    except Exception as e:
        logging.error(f"Query not unsuccessful due to {e}. Return empty DataFrame.")

    return df_related_queries


def process_related_query_response(response, kw, geo, ranking):
    """ Helper function for unpack_related_queries_response() """
    try:
        df = response[kw][ranking]
        df[["keyword", "ranking", "geo", "query_timestamp"]] = [
            kw,
            ranking,
            geo,
            datetime.now(),
        ]
    except:
        logging.info(f"Append empty dataframe for {ranking}: {kw}")
        return pd.DataFrame(
            columns=["query", "value", "keyword", "ranking", "geo", "query_timestamp"]
        )

    return df


def unpack_related_queries_response(response):
    """Unpack response from dictionary and create one dataframe for each ranking and each keyword """
    assert isinstance(response, dict), "Empty response. Try again."

    ranking = [*response[[*response][0]]]
    keywords = [*response]

    return response, ranking, keywords


def create_related_queries_dataframe(
    response, rankings, keywords, geo_description="global"
):
    """Returns a single dataframe of related queries for a list of keywords
    and each ranking (either 'top' or 'rising')
    """
    df_list = []
    for r in rankings:
        for kw in keywords:
            df_list.append(
                process_related_query_response(
                    response, kw=kw, ranking=r, geo=geo_description
                )
            )

    return pd.concat(df_list)


def get_related_queries_pipeline(
    pytrends_session, keyword_list, cat=0, geo="", geo_description="global"
):
    """Returns all response data for pytrend's .related_queries() in a single dataframe

    Example usage:

        pytrends_session = create_pytrends_session()
        df = get_related_queries_pipeline(pytrends_session, keyword_list=['pizza', 'lufthansa'])
    """
    response = get_related_queries(
        pytrends_session=pytrends_session, keyword_list=keyword_list, cat=cat, geo=geo
    )  #
    response, rankings, keywords = unpack_related_queries_response(response=response)
    df_trends = create_related_queries_dataframe(
        response=response,
        rankings=rankings,
        keywords=keywords,
        geo_description=geo_description,
    )

    return df_trends


# ----------------------------------------------------------
# Google trends: Interest over time
# ----------------------------------------------------------


def process_interest_over_time(
    df_query_result, keywords, date_index=None, query_length=261
):
    """Process query results
            * check for empty response --> create df with 0s if empty
            * drop isPartial rows and column
            * transpose dataframe to wide format (keywords//search interest)

    Args:
        df_query_result (pd.DataFrame): dataframe containing query result (could be empty)
        date_index (pd.Series): series with date form a basic query to construct df for empty reponses

    Returns:
        Dataframe: contains query results in long format
        (rows: keywords, columns: search interest over time)
    """
    # non-empty df
    if df_query_result.shape[0] != 0:
        # reset_index to preserve date information, drop isPartial column
        df_query_result_processed = df_query_result.reset_index().drop(
            ["isPartial"], axis=1
        )

        df_query_result_long = pd.melt(
            df_query_result_processed,
            id_vars=["date"],
            var_name="keyword",
            value_name="search_interest",
        )

        # long format (date, keyword, search interest)
        return df_query_result_long

    # empty df: no search result for any keyword
    else:
        # create empty df with 0s
        query_length = len(date_index) if date_index is not None else query_length

        df_zeros = pd.DataFrame(
            np.zeros((query_length * len(keywords), 3)),
            columns=["date", "keyword", "search_interest"],
        )
        # replace 0s with dates
        df_zeros["date"] = (
            pd.concat([date_index for i in range(len(keywords))], axis=0).reset_index(
                drop=True
            )
            if date_index is not None
            else 0
        )
        # replace 0s with keywords
        df_zeros["keyword"] = np.repeat(keywords, query_length)

        return df_zeros


def query_interest_over_time(keywords, date_index=None, timeframe="today 5-y"):
    """Forward keywords to Google Trends API and process results into long format

    Args:
        keywords (list): list of keywords, with maximum length 5

    Returns:
        DataFrame: Search interest per keyword, preprocessed by process_interest_over_time()

    """
    # init pytrends
    pt = create_pytrends_session()
    pt.build_payload(kw_list=keywords, timeframe=timeframe)

    # load search interest over time
    df_query_result_raw = pt.interest_over_time()

    # preprocess query results
    df_query_result_processed = process_interest_over_time(
        df_query_result_raw, keywords, date_index
    )

    return df_query_result_processed


def get_query_date_index(timeframe="today 5-y"):
    """Queries Google trends to have a valid index for query results that returned an empty dataframe
    Args:
        timeframe (string):

    Returns:
        pd.Series: date index of Google trend's interest_over_time()
    """

    # init pytrends with query that ALWAYS works
    pt = create_pytrends_session()
    pt.build_payload(kw_list=["pizza", "lufthansa"], timeframe=timeframe)
    df = pt.interest_over_time()

    # set date as column
    df = df.rename_axis("date").reset_index()

    return df.date


# ---------------------------------------------------
# MAIN QUERY FUNCTION
# ---------------------------------------------------


def get_interest_over_time(
    keyword_list,
    filepath,
    filepath_failed,
    timeframe="today 5-y",
    max_retries=3,
    timeout=10,
):
    """Workhorse function to query Google Trend's interest_over_time() function.
    It respects the query's requirements like
        * max. 5 keywords per query, handled by list_batch()
        * a basic date index for queries returning empty dataframe
        * randomized timeout to not bust rate limits

    Error handling:
        * retry after query error with increased timeout
        * when a query fails after retries, related keywords are stored in csv in filepath_failed.



    Args:
        keyword_list (list): strings used for the google trends query
        filepath (string): csv to store successful query results
        filepath_failed (string): csv to store unsuccessful keywords
        max_retries (int): how often retry
        timeout (int): time to wait in seconds btw. queries

    Returns:
        None: Writes dataframe to csv
    """
    # get basic date index for empty responses
    date_index = get_query_date_index(timeframe=timeframe)

    # divide list into batches of max 5 elements (requirement from Gtrends)
    kw_batches = list_batch(lst=keyword_list, n=5)

    for i, kw_batch in enumerate(kw_batches):
        # retry until max_retries reached
        for attempt in range(max_retries):

            # random int from range around timeout
            timeout_randomized = randint(timeout - 3, timeout + 3)
            try:
                df = query_interest_over_time(kw_batch, date_index=date_index)

            # query unsuccessful
            except Exception as e:
                logging.error(
                    f"query_interest_over_time() failed in get_interest_over_time with: {e}"
                )
                timeout += 3  # increase timetout to be safe
                sleep_countdown(timeout_randomized, print_step=2)

            # query was successful: store results, sleep
            else:
                logging.info(
                    f"{i+1}/{len(list(kw_batches))} get_interest_over_time() query successful"
                )
                df_to_csv(df, filepath=filepath)
                sleep_countdown(timeout_randomized)
                break

        # max_retries reached: store index of unsuccessful query
        else:
            df_to_csv(pd.DataFrame(kw_batch), filepath=filepath_failed)
            logging.warning(f"{kw_batch} appended to unsuccessful_queries")
