"""
Extract data from Google trends with the pytrends package

    methods take one keyword, call pytrends and return raw data 

"""

import pandas as pd
from pytrends.request import TrendReq
import logging

def get_queries(keyword):
    """ Calls pytrend' related_queries with a list of keywords and geo settings 
    
    Args:
        pytrend (object): TrendReq() session of pytrend
        keyword (str): list of strings, used as input for query and passed to TrendReq().build_payload() 
    
    Returns:
        Dataframe with query result
    """    
    assert isinstance(keyword, str), f"Keyword should be string. Instead of type {type(keyword)}"

    df_related_queries = pd.DataFrame()

    try:
        pytrend = TrendReq() 

        pytrend.build_payload(keyword)
        df_related_queries = pytrend.related_queries()

        print(f"Query succeeded for", *keyword, sep='\n\t')
    except Exception as e:
        print(e, "\nQuery not unsuccessful. Return empty DataFrame.\n", '='*42)

    return df_related_queries