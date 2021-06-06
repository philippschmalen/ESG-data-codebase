"""
Extract results count from Google with beautiful soup

Methods take a list of keywords and return a dataframe.

"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_search_url(keyword_list, url="https://www.google.com/search?q="):
    """Create Google search URL for a keyword from keyword_list

    Args:
        keyword_list (list): list of strings that contain the search keywords
        url (str): Google's base search url

    Returns:
        list: Google search url like https://www.google.com/search?q=pizza

    """
    search_query = [kw.replace(" ", "+") for kw in keyword_list]  # replace space with '+'
    return [url + sq for sq in search_query]


def get_results_count(keyword, user_agent):
    """Gets Google's result count for a keyword

    Args:
        keyword (string): The keyword for which to get the results count
        user_agent (string): For example {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}

    Returns:
        int: Results count
    """
    result = requests.get(keyword, headers=user_agent)
    soup = BeautifulSoup(result.content, "html.parser")

    #  string that contains results count 'About 1,410,000,000 results'
    total_results_text = soup.find("div", {"id": "result-stats"}).find(text=True, recursive=False)

    # extract number
    results_num = int("".join([num for num in total_results_text if num.isdigit()]))

    return results_num


def get_results_count_pipeline(keyword_list, user_agent, url="https://www.google.com/search?q="):
    """Google results count for each keyword of keyword_list in a dataframe

    Args:
        keyword_list (list): The keywords for which to get the results count
        user_agent (string): For example {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
        url (string): Google's base search URL like "https://www.google.com/search?q=" (default)

    Returns:
        dataframe: Google results count and query metadata

    Examples:

        # TODO conform with doctest
        >> with open('../settings.yaml') as file:
           config = yaml.full_load(file)
        >> user_agent = config['query']['google_results']['user_agent']
        >> base_url = config['query']['google_results']['base_url']
        >> keyword_list = ['pizza', 'lufthansa']
        >> result_counts = get_results_count_pipeline(keyword_list, user_agent, base_url)
    """
    search_urls = create_search_url(keyword_list)
    result_count = [get_results_count(url, user_agent) for url in search_urls]

    df = pd.DataFrame(
        {
            "keyword": keyword_list,
            "results_count": result_count,
            "search_url": search_urls,
            "query_timestamp": datetime.now(),
        }
    )
    # testing
    assert_google_results(df=df, keyword_list=keyword_list, url=url)

    return df


def assert_google_results(df, keyword_list, url="https://www.google.com/search?q="):
    """Ensures that dataframe meets expectations """

    # expected dataframe for comparison
    df_compare = pd.DataFrame(
        {
            "keyword": pd.Series([*keyword_list], dtype="object"),
            "results_count": pd.Series([1 for i in keyword_list], dtype="int64"),
            "search_url": pd.Series(create_search_url(keyword_list, url=url), dtype="object"),
            "query_timestamp": pd.Series([datetime.now() for i in keyword_list], dtype="datetime64[ns]"),
        }
    )

    # comparison to actual
    column_difference = set(df.columns).symmetric_difference(df_compare.columns)
    assert len(column_difference) == 0, f"The following columns differ to reference dataframe: {column_difference}"
    assert (df_compare.dtypes == df.dtypes).all(), f"Different dtypes for {df.dtypes}\n{df_compare.dtypes}"
    assert len(df) == len(keyword_list), f"{len(df)} does not equal {len(keyword_list)}"

    logging.info("Google results data meets expectations")
    # TODO how about using df.equal(), less verbose
