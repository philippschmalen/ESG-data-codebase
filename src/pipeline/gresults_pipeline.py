from typing import Tuple, Any, List
import requests
import pandas as pd
from datetime import datetime
import yaml

import prefect
from prefect import task, Parameter, Flow, unmapped, apply_map
from prefect.executors import LocalDaskExecutor
from bs4 import BeautifulSoup


SETTINGS = "settings.yaml"


def prefect_logger():
    logger = prefect.context.get("logger")
    logger.setLevel("DEBUG")
    return logger


@task
def load_settings(settings_file) -> Tuple[Any, str, List[str]]:
    with open(settings_file) as file:
        config = yaml.full_load(file)
    user_agent = config["query"]["google_results"]["user_agent"]
    base_url = config["query"]["google_results"]["base_url"]
    keyword_list = ["pizza", "lufthansa"]
    return user_agent, base_url, keyword_list


@task
def create_search_url(base_url, keyword_list):
    """Create Google search URL for a keyword from keyword_list

    Args:
        keyword_list (list): list of strings that contain the search keywords
        base_url (str): Google's base search url

    Returns:
        list: Google search url like https://www.google.com/search?q=pizza

    """
    search_kw = [kw.replace(" ", "+") for kw in keyword_list]  # replace space with '+'
    search_query = [base_url + sq for sq in search_kw]
    return search_query


@task
def get_results_count(user_agent, query) -> int:
    """Gets Google's result count for a keyword

    Args:
        keyword (string): The keyword for which to get the results count
        user_agent (string): For example {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like
            Gecko) Chrome/80.0.3987.149 Safari/537.36"}

    Returns:
        int: Results count
    """
    result = requests.get(query, headers=user_agent)
    soup = BeautifulSoup(result.content, "html.parser")

    #  string that contains results count 'About 1,410,000,000 results'
    total_results_text = soup.find("div", {"id": "result-stats"}).find(
        text=True, recursive=False
    )

    # extract number
    results_num = int("".join([num for num in total_results_text if num.isdigit()]))
    return results_num


@task
def get_results_df(base_url, keyword_list, search_urls, search_counts):
    """Google results count for each keyword of keyword_list in a dataframe

    Args:
        keyword_list (list): The keywords for which to get the results count

    Returns:
        dataframe: Google results count and query metadata

    """

    df = pd.DataFrame(
        {
            "keyword": keyword_list,
            "results_count": search_counts,
            "search_url": search_urls,
            "query_timestamp": datetime.now(),
        }
    )
    return df


@task
def assert_google_results(df, keyword_list, search_urls):
    """Ensures that dataframe meets expectations"""

    # expected dataframe for comparison
    df_compare = pd.DataFrame(
        {
            "keyword": pd.Series([*keyword_list], dtype="object"),
            "results_count": pd.Series([1 for i in keyword_list], dtype="int64"),
            "search_url": pd.Series(search_urls, dtype="object"),
            "query_timestamp": pd.Series(
                [datetime.now() for i in keyword_list], dtype="datetime64[ns]"
            ),
        }
    )

    # comparison to actual
    column_difference = set(df.columns).symmetric_difference(df_compare.columns)
    assert (
        len(column_difference) == 0
    ), f"The following columns differ to reference dataframe: {column_difference}"
    assert (
        df_compare.dtypes == df.dtypes
    ).all(), f"Different dtypes for {df.dtypes}\n{df_compare.dtypes}"
    assert len(df) == len(keyword_list), f"{len(df)} does not equal {len(keyword_list)}"

    prefect_logger().info("Google results data meets expectations")


@task
def print_result(results_df):
    print(results_df.head())


with Flow("gresults") as flow:
    user_agent, base_url, keyword_list = load_settings(SETTINGS)
    search_urls = create_search_url(base_url, keyword_list)
    prefect_logger().info(f"created search_urls as {search_urls}")
    search_counts = apply_map(
        get_results_count, user_agent=unmapped(user_agent), query=search_urls
    )
    results_df = get_results_df(base_url, keyword_list, search_urls, search_counts)
    assert_google_results(results_df, keyword_list, search_urls)
    print_result(results_df)

if __name__ == "__main__":
    flow.executor = LocalDaskExecutor(scheduler="threads", num_workers=4)
    flow.run()
