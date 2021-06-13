# -*- coding: utf-8 -*-
import streamlit as st

import logging
from datetime import datetime
import plotly.express as px
import chart_studio.plotly as cs
import tsf_plots

from pytickersymbols import PyTickerSymbols
import data.yahoofinance_extract as yq
from data.gtrends_extract import get_interest_over_time
from data.utilities import timestamp_now

esg_df = yq.esg_firm_query_keywords_pipeline(index_name="DAX", path_to_settings="../settings.yaml")
indices = PyTickerSymbols().get_all_indices()

trends_df = get_interest_over_time(
    keyword_list=esg_df.query_keyword[:100],
    filepath=f"../data/raw/dax_search_interest_{timestamp_now()}.csv",
    filepath_failed=f"../data/raw/failed_dax_search_interest_{timestamp_now()}.csv",
)

st.stop()

# ---------------------------------------------------
# VISUALS
# ---------------------------------------------------


timeframe = f'2016-12-14 {datetime.now().strftime("%Y-%m-%d")}'
date_index = get_query_date_index(timeframe=timeframe)
df_search_interest = query_googletrends(keyword_list, date_index=date_index, timeframe=timeframe)
"", df_search_interest.set_index("date").resample("M")


def plot_interest_over_time(df):
    """line chart: weekly change of Google trends """
    fig = px.line(
        df,
        x="date",
        y="search_interest",
        color="keyword",
        line_shape="spline",
        title="Search interest over time",
        labels={"date": "", "keyword": "", "search_interest": "Search interest"},
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
deploy_figure(figure=fig, filename="gtrends_greenwashing_sf")
