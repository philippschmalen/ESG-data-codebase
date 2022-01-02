"""
Retrieve firm-level esg scores, process firm names and construct query strings
"""
from yahooquery import Ticker
from pytickersymbols import PyTickerSymbols
import logging
import numpy as np
import pandas as pd
import re
import yaml


# ---------------------------------------------------
# INDEX DETAILS
# ---------------------------------------------------


def get_index_stock_details(pytickersymbols, index_name):
    """Get firm name, stock ticker for a specified stock index.
    Available indices from pytickersymbols: PyTickerSymbols().get_all_indices()
    See https://github.com/portfolioplus/pytickersymbols for package details

    Args:
        pytickersymbols (object): Init object from PyTickerSymbols()
        index_name (str): Index name from PyTickerSymbols().get_all_indices()

    Returns:
        Dataframe:
    """
    index_details = pd.DataFrame(pytickersymbols.get_stocks_by_index(index_name))

    # string encoding
    try:
        index_details.name = index_details.name.str.encode("latin-1").str.decode(
            "utf-8"
        )
    except Exception:
        logging.warning(f"Encoding error for {index_name}")
        index_details.name = index_details.name.str.encode("utf-8").str.decode("utf-8")

    # retrieve yahoo ticker symbol
    index_details["yahoo_ticker"] = index_details.symbols.apply(
        lambda x: x[0]["yahoo"] if len(x) > 1 else np.nan
    )
    index_details.yahoo_ticker.fillna(index_details.symbol, inplace=True)

    # set ticker as index
    index_details.set_index("yahoo_ticker", inplace=True, drop=False)
    index_details.drop(columns=["id"], inplace=True)

    return index_details


# ---------------------------------------------------
# FIRM-LEVEL ESG DATA
# ---------------------------------------------------


def get_esg_details(yahoo_ticker):
    """Returns esg information for suitable yahoo ticker which can be string, pd.Series or list"""

    # convert series to list
    if isinstance(yahoo_ticker, pd.Series):
        yahoo_ticker = yahoo_ticker.to_list()

    ticker_details = Ticker(yahoo_ticker)
    esg_df = pd.DataFrame(ticker_details.esg_scores).T

    return esg_df


def get_index_firm_esg(pytickersymbols, index_name):
    """Merge index, firm name and esg data"""
    index_stocks = get_index_stock_details(
        pytickersymbols=pytickersymbols, index_name=index_name
    )
    esg_details = get_esg_details(yahoo_ticker=index_stocks.yahoo_ticker)

    stocks_esg = pd.concat([index_stocks, esg_details], axis=1)

    return stocks_esg


def replace_firm_names(df, settings_path):
    """Replace firm names as specified in settings.yaml"""

    with open(settings_path, encoding="utf8") as file:
        settings = yaml.full_load(file)

    try:
        settings["query"]["firm_name"]
    except Exception:
        logging.warning(
            "No firm names specified in settings['query']['firm_name']. \
        Firm names still contain legal suffix which compromises search results."
        )
    assert (
        "name" in df.columns
    ), "Dataframe has no name column. Firm names cannot be replaced."

    replace_firm_names = settings["query"]["firm_names"]
    df["firm_name"] = df.name.replace(replace_firm_names, regex=True)
    return df


def remove_missing_esg_firms(esg_df, missing_placeholder="No fundamentals data"):
    """Drops firms that have no ESG scores. Placeholder from Yahoo"""
    return esg_df.loc[~esg_df.peerGroup.str.contains(missing_placeholder)]


def get_esg_controversy_keywords(settings_path):
    """Load controversy keywords from settings.yaml"""

    with open(settings_path, encoding="utf8") as file:
        settings = yaml.full_load(file)

    controversies = settings["esg"]["negative"]

    return controversies


def create_query_keywords(esg_df, keyword_list, explode=True):
    """Construct query keywords from firm_name and a list of keywords

    Args:
        esg_df (Dataframe): Data from yahooquery Ticker(yahoo_ticker).esg_scores, processed firm names
        keyword_list (list): list of strings that are attached to each firm name
        explode (boolean): If true re-shapes to logn format with each row having a unique query_keyword

    Returns:
        Dataframe: added query_keyword column (firm_name + keyword)

    """
    esg_df["query_keyword"] = esg_df.firm_name.apply(
        lambda x: [x + kw for kw in keyword_list]
    )

    if explode:
        return esg_df.explode(column="query_keyword")
    else:
        return esg_df


def esg_firm_query_keywords_pipeline(index_name, path_to_settings):
    """ESG scores, processed firm names and firm name query strings in a dataframe.

    Args:
        index_name (string): Index name, one of PyTickerSymbols().get_all_indices()
        path_to_settings (string): path to settings.yaml, where all esg keywords are specified

    Returns:
        Dataframe: esg scores and related data from Yahoo!Finance incl. processed firm names and query keywords

    """
    pytickersymbols = PyTickerSymbols()
    controversy_keywords = get_esg_controversy_keywords(path_to_settings)
    esg_df = (
        get_index_firm_esg(pytickersymbols=pytickersymbols, index_name=index_name)
        .pipe(replace_firm_names, settings_path=path_to_settings)
        .pipe(remove_missing_esg_firms)
        .pipe(create_query_keywords, keyword_list=controversy_keywords)
    )

    return esg_df
