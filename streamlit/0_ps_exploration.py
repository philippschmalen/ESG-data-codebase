import streamlit as st
import plotly.express as px
import chart_studio.plotly as cs
import logging

import pandas as pd
import numpy as np

import sys
sys.path.append('../src/data')
sys.path.append('../src/visualization')

from gtrends_extract import (create_pytrends_session, 
                            get_interest_over_time)

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



# #--------------------------------------------------- 
# # main function
# #---------------------------------------------------

keyword_list = ['abott labor strike', 'CenterPoint Energy greenwashing', 'abott greenwashing', 'abott transparency']

'', get_interest_over_time(keyword_list=keyword_list, 
    filepath='../data/raw/gtrend_test.csv', 
    filepath_failed='../data/raw/gtrend_test_failed.csv', max_retries=1, timeout=5)

# date_index = get_query_date_index()
# '', query_googletrends(keywords=keyword_list, date_index=date_index)
# works --> rather append 

                # 'abott labor strike',
                # 'sustainable finance', 'MSCI', 'ESG', 'lufthansa', 'pizza'] 
# get_interest_over_time(keyword_list=keyword_list, 
#     filepath='../data/raw/gtrends_test_query.csv', 
#     filepath_unsuccessful='../data/raw/gtrends_test_query_unsuccessful.csv')

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
