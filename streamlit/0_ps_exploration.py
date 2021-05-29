import streamlit as st
import plotly.express as px
import chart_studio.plotly as cs
import logging

import pandas as pd
import numpy as np

import sys
sys.path.append('../src/data')
sys.path.append('../src/visualization')
from gtrends_extract import create_pytrends_session 


import os
import sys
from time import sleep
from random import randint 

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



def query_googletrends(keywords, date_index=None, timeframe='today 5-y'):
    """Forward keywords to Google Trends API and process results into long format

    Args
        keywords: list of keywords, with maximum length 5

    Return
        DataFrame with search interest per keyword, preprocessed by handle_query_results()

    """
    # initialize pytrends
    pt = create_pytrends_session()

    # pass keywords to api
    pt.build_payload(kw_list=keywords, timeframe=timeframe) 

    # retrieve query results: search interest over time
    df_query_result_raw = pt.interest_over_time()

    # preprocess query results
    df_query_result_processed = handle_query_results(df_query_result_raw, keywords, date_index)

    return df_query_result_processed


def get_query_date_index(timeframe='today 5-y'):
    """Queries Google trends to have a valid index for query results that returned an empty dataframe

    Returns:
        pd.Series: date index of Google trend's interest_over_time()
    """
    
    # init pytrends with query that ALWAYS works
    pt = create_pytrends_session()
    pt.build_payload(kw_list=['pizza', 'lufthansa'], timeframe=timeframe)
    df = pt.interest_over_time()

    # set date as column
    df = df.rename_axis('date').reset_index()


    return df.date

#---------------------------------------------------
# -- UTILITIES
# 
# list_flatten: flatten list
# n_batch: generator for n-sized list batches
# list_batch: get n-sized chunks from n_batch generator
# df_to_csv: write csv
# timestamp_now: get string  
# sleep_countdown(): countdown in console
# 
#---------------------------------------------------

def list_flatten(nested_list):
    """Flattens nested list"""
    return [element for sublist in nested_list for element in sublist]

def n_batch(lst, n=5):
    """Yield successive n-sized chunks from list lst
    
    Args
        lst: list 
        n: selected batch size
        
    Returns 
        List: lst divided into batches of len(lst)/n lists
    """
    
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def list_batch(lst, n=5):
    """"Divides a list into a list of lists with n-sized length"""
    return list(n_batch(lst=lst, n=n))


def df_to_csv(df, filepath):
    """Export df to CSV. If it exists already, append data."""
    # file does not exist --> write header
    if not os.path.isfile(f'{filepath}'):
        df.to_csv(f'{filepath}', index=False)
    # file exists --> append data without header
    else:
        df.to_csv(f'{filepath}', index=False, header=False, mode='a')

def timestamp_now():
    """Create timestamp string in format: yyyy/mm/dd-hh/mm/ss"""
    
    timestr = strftime("%Y%m%d-%H%M%S")
    timestamp = '{}'.format(timestr)  
    
    return timestamp

def sleep_countdown(duration, print_step=2):
    """Sleep for certain duration and print remaining time in steps of print_step
    
    Input
        duration: duration of timeout (int)
        print_step: steps to print countdown (int)

    Return 
        None
    """
    for i in range(duration,0,-print_step):
        sleep(print_step)
        sys.stdout.write(str(i-print_step)+' ')
        sys.stdout.flush()

#--------------------------------------------------- 
# main function
#---------------------------------------------------

def get_interest_over_time(keyword_list, filepath, filepath_unsuccessful, timeframe='today 5-y', max_retries=3, timeout=20):
    """  
    Args:
        max_retries: number of maximum retries
    Returns:
        None: Writes dataframe to csv
    """
    # get basic date index for empty responses
    date_index = get_query_date_index(timeframe=timeframe)

    # keywords in batches of 5
    kw_batches = list_batch(lst=keyword_list, n=5)


    for kw_batch in kw_batches: 
        # retry until max_retries reached
        for attempt in range(max_retries): 

            # random int from range around timeout 
            timeout_randomized = randint(timeout-3,timeout+3)
            try:
                df = query_googletrends(kw_batch, date_index=date_index)
            
            # query unsuccessful
            except Exception as e:
                timeout += 3 # increase timetout to be safe
                sleep_countdown(timeout_randomized, print_step=2)
            

            # query was successful: store results, sleep 
            else:
                df_to_csv(df, filepath=filepath)
                sleep_countdown(timeout_randomized)
                break

        # max_retries reached: store index of unsuccessful query
        else:
            df_to_csv(pd.DataFrame(kw_batch), filepath=filepath_unsuccessful)
            logging.warning(f"{kw_batch} appended to unsuccessful_queries")


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



# NEXT: check how empty responses can be added to dataframe
# RUN: query_googletrends and check output
keyword_list = ['abott labor strike', 'CenterPoint Energy greenwashing', 'abott greenwashing', 
                'abott transparency']
date_index = get_query_date_index()
'', query_googletrends(keywords=keyword_list, date_index=date_index)
                # 'abott labor strike',
                # 'sustainable finance', 'MSCI', 'ESG', 'lufthansa', 'pizza'] 
# get_interest_over_time(keyword_list=keyword_list, 
#     filepath='../data/raw/gtrends_test_query.csv', 
#     filepath_unsuccessful='../data/raw/gtrends_test_query.csv')

st.stop()








#---------------------------------------------------
# VISUALS
#---------------------------------------------------
from datetime import datetime
timeframe = f'2016-12-14 {datetime.now().strftime("%Y-%m-%d")}' 
date_index = get_query_date_index(timeframe=timeframe)
df_search_interest =  query_googletrends(keyword_list, date_index=date_index, timeframe=timeframe)
'', df_search_interest.set_index('date').resample('M')

import tsf_plots

def plot_interest_over_time(df):
    """line chart: weekly change of Google trends """
    fig = px.line(df, x="date", y="search_interest", color="keyword", 
                    line_shape='spline',
                  title='Search interest over time', 
                 labels={
                         "date": "",
                         "keyword": "", 
                         "search_interest": "Search interest"
                     },
                  # text = df.keyword
                 )
    # fig.update_traces(mode="markers+lines", hovertemplate="%{text}<br>" + "%{y:20.0f}Mio.<br>%{x}<extra></extra>") 
    
    # -- customize legend
    fig.update_layout(
        # legend=dict(
        # orientation="v",
        # yanchor="bottom",
        # y=0.9,
        # xanchor="right", 
        # x=0.5, 
        # bgcolor='rgba(0,0,0,0)'), # transparent  
        hovermode="closest",
    )
    return fig

def deploy_figure(figure, filename):    
    """ Upload graph to chartstudio """
    logging.info(f"Upload {filename} figure to plotly")
    cs.plot(figure, filename=filename)


tsf_plots.set_layout_template()
fig = plot_interest_over_time(df_search_interest)
st.plotly_chart(fig)
deploy_figure(figure=fig, filename='gtrends_greenwashing_sf')
