import streamlit as st

import pandas as pd
import numpy as np

import sys
sys.path.append('../src/data')
from gtrends_extract import create_pytrends_session 


def handle_query_results(df_query_result, keywords, date_index=None, query_length=261):
    """Process query results: 
            (i) check for empty response --> create df with 0s if empty
            (ii) drop isPartial rows and column
            (iii) transpose dataframe to wide format (keywords//search interest)

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
        df_query_result_processed = df_query_result.reset_index()\
            .drop(['isPartial'], axis=1)

        df_query_result_long = pd.melt(df_query_result_processed, id_vars=['date'], var_name='keyword', value_name='search_interest')

        # long format (date, keyword, search interest)
        return df_query_result_long

    # empty df: no search result for any keyword
    else:        
        # create empty df with 0s
        query_length = len(date_index) if date_index is not None else query_length

        df_zeros = pd.DataFrame(np.zeros((query_length*len(keywords), 3)), columns=['date','keyword', 'search_interest'])
        # replace 0s with dates
        df_zeros['date'] = pd.concat([date_index for i in range(len(keywords))], axis=0).reset_index(drop=True) if date_index is not None else 0
        # replace 0s with keywords 
        df_zeros['keyword'] = np.repeat(keywords, query_length)


        return df_zeros



def query_googletrends(keywords, date_index=None):
    """Forward keywords to Google Trends API and process results into long format

    Args
        keywords: list of keywords, with maximum length 5

    Return
        DataFrame with search interest per keyword, preprocessed by handle_query_results()

    """
    # initialize pytrends
    pt = create_pytrends_session()

    # pass keywords to api
    pt.build_payload(kw_list=keywords) 

    # retrieve query results: search interest over time
    df_query_result_raw = pt.interest_over_time()

    # preprocess query results
    df_query_result_processed = handle_query_results(df_query_result_raw, keywords, date_index)

    return df_query_result_processed


def get_basic_query_date():
    """Queries Google trends to have a valid index for query results that returned an empty dataframe

    Returns:
        pd.Series: date index of Google trend's interest_over_time()
    """
    
    # init pytrends with query that ALWAYS works
    pt = create_pytrends_session()
    pt.build_payload(kw_list=['pizza', 'lufthansa'])
    df = pt.interest_over_time()

    # set date as column
    df = df.rename_axis('date').reset_index()


    return df.date



keyword_list = [    'Avery Dennison greenwashing', 'Avery Dennison force labor'] # 'lufthansa', 'pizza', 
date_index = get_basic_query_date()
'', query_googletrends(keyword_list, date_index=date_index)
# TODO: 


# initialize pytrends
# pt = create_pytrends_session()
# # pass keywords to api
# pt.build_payload(kw_list=keyword_list) 
# df_raw = pt.interest_over_time()
















from time import sleep
from random import randint # for random timeout +/- 5

def query(keywords, filepath, filename, max_retries=1, idx_unsuccessful=list(), timeout=20) :
    """Handle failed query and handle raised exceptions
    
    Input
        keywords: list with keywords for which to retrieve news
        max_retries: number of maximum retries
        until_page: maximum number of retrievd news page
        
    
    Return
        Inidces where max retries were reached
    """    
    # retry until max_retries reached
    for attempt in range(max_retries):   

        # random int from range around timeout 
        timeout_randomized = randint(timeout-3,timeout+3)

        try:
            df_result = query_googletrends(keywords)


        # handle query error
        except Exception as e:

            # increase timeout
            timeout += 5

            print(">>> EXCEPTION at {}: {} \n Set timeout to {}\n".format(i, e, timeout))
            # sleep
            h.sleep_countdown(timeout_randomized, print_step=2)


        # query was successful: store results, sleep 
        else:

            # generate timestamp for csv
            stamp = h.timestamp_now()

            # merge news dataframes and export query results
            h.make_csv(df_result, filename, filepath, append=True)

            # sleep
            h.sleep_countdown(timeout_randomized)
            break

    # max_retries reached: store index of unsuccessful query
    else:
        h.make_csv(pd.DataFrame(keywords), "unsuccessful_queries.csv", filepath, append=True)
        print("{} appended to unsuccessful_queries\n".format(keywords))
