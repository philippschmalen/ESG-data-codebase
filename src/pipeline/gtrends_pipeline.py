from typing import Tuple, Any, List
from prefect import task, Parameter, Flow
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
from root_logger import logger

logger = logger()


@task
def create_pytrends_session():
    """Create pytrends TrendReq() session on which .build_payload() can be called."""
    return TrendReq()


@task
def get_response(
    pytrends_session: TrendReq, keyword_list: List[str], cat: int = 0, geo: str = ""
) -> dict:
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

    pytrends_session.build_payload(keyword_list, cat=cat, geo=geo)
    response = pytrends_session.related_queries()
    if response is not None:
        logger.info(f"Query succeeded for {*keyword_list ,}")
    else:
        logger.warning(
            f"Query failed for {*keyword_list ,}, obtained df_related_queries is None."
        )

    return response


@task
def unpack_response(response: dict) -> Tuple[Any, List[str]]:
    """Unpack response from dictionary and fetch ranking and keywords."""
    assert isinstance(response, dict), "Empty response. Try again."

    rankings = [*response[[*response][0]]]
    keywords = [*response]
    return rankings, keywords


@task
def get_df_response(response: dict, rk: Any, kw: str, geo="global") -> pd.DataFrame:
    """Helper function for unpack_related_queries_response()"""
    # TODO combine this into create_df_trends. In principle, no need to fetch df one row by another, this is very not
    #  "pandas"
    try:
        df = response[kw][rk]
        df[["keyword", "ranking", "geo", "query_timestamp"]] = [
            kw,
            rk,
            geo,
            datetime.now(),
        ]
        return df
    except KeyError:
        logger.warning(f"Append empty dataframe for {rk}: {kw}")
        return pd.DataFrame(
            columns=["query", "value", "keyword", "ranking", "geo", "query_timestamp"]
        )


@task
def create_df_trends(response: dict, rankings: Any, keywords: List[str]) -> pd.DataFrame:
    """Returns a single dataframe of related queries for a list of keywords
    and each ranking (either 'top' or 'rising')
    """
    df_list = []
    for rk in rankings:
        for kw in keywords:
            df_list.append(get_df_response(response, rk, kw))
    return pd.concat(df_list)


with Flow("gtrends") as flow:
    KEYWORDS = Parameter("keywords", default=[])
    GEO = Parameter("geo", default="")
    CAT = Parameter("cat", default=0)

    session = create_pytrends_session()
    response = get_response(session, KEYWORDS, CAT, GEO)
    rankings, keywords = unpack_response(response)
    df_trends = create_df_trends(response, rankings, keywords)
