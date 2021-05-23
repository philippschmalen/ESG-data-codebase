"""
Extract data from Google trends with the pytrends package

    methods take one keyword, call pytrends and return raw data 

"""

import pandas as pd
import logging
from datetime import datetime
from pytrends.request import TrendReq


def create_pytrends_session():
    """Create pytrends TrendReq() session on which .build_payload() can be called """
    pytrends_session = TrendReq() 

    return pytrends_session

def get_related_queries(pytrends_session, keyword_list, cat=0, geo=''):
    """Returns a dictionary with a dataframe for each keyword 
        Calls pytrend's related_queries()
    
    Args:
        pytrends_session (object): TrendReq() session of pytrend
        keyword_list (list): Used as input for query and passed to TrendReq().build_payload() 
        cat (int): see https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories 
        for all categories
        geo (str): Geolocation like US, UK

    Returns:
        Dictionary: Dict with dataframes with related query results 
    """    
    assert isinstance(keyword_list, list), f"keyword_list should be string. Instead of type {type(keyword_list)}"

    df_related_queries = pd.DataFrame()

    try:
        pytrends_session.build_payload(keyword_list, cat=cat, geo=geo)
        df_related_queries = pytrends_session.related_queries()
        logging.info(f"Query succeeded for {*keyword_list ,}")

    except Exception as e:
        logging.error(f"Query not unsuccessful due to {e}. Return empty DataFrame.")

    return df_related_queries

def process_response(response, kw, geo, ranking):
    """ Helper function for unpack_related_queries_response() """
    try:
        df = response[kw][ranking]
        df[['keyword', 'ranking', 'geo', 'query_timestamp']] = [
            kw, ranking, geo, datetime.now()]
    except:
        logging.info(f"Append empty dataframe for {ranking}: {kw}")
        return pd.DataFrame(columns=['query', 'value', 'keyword', 'ranking', 'geo', 'query_timestamp'])

    return df

def unpack_related_queries_response(response):
    """Unpack response from dictionary and create one dataframe for each ranking and each keyword """
    assert isinstance(response, dict), "Empty response. Try again."

    ranking = [*response[[*response][0]]]
    keywords = [*response]

    return response, ranking, keywords

def create_related_queries_dataframe(response, rankings, keywords, geo_description='global'):
    """Returns a single dataframe of related queries for a list of keywords
    and each ranking (either 'top' or 'rising') """
    df_list = []
    for r in rankings:
        for kw in keywords:
            df_list.append(process_response(
                response, kw=kw, ranking=r, geo=geo_description))

    return pd.concat(df_list)

def get_related_queries_pipeline(pytrends_session, keyword_list, cat=0, geo='', geo_description='global'): 
    """Returns all response data for pytrend's .related_queries() in a single dataframe
    Usage: 
        pytrends_session = create_pytrends_session()
        df = get_related_queries_pipeline(pytrends_session, keyword_list=['pizza', 'lufthansa'])
    """
    response = get_related_queries(pytrends_session=pytrends_session, keyword_list=keyword_list, cat=cat, geo=geo) # 
    response, rankings, keywords  = unpack_related_queries_response(response=response)
    df_trends = create_related_queries_dataframe(
        response=response, 
        rankings=rankings, 
        keywords=keywords, 
        geo_description=geo_description)
    
    return df_trends