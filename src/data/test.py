import pandas as pd
import numpy as np
from gtrends_extract import get_query_date_index

if __name__ == "__main__":
    query_length = 261
    keywords = [
        "adidas manipulation",
        "adidas dispute",
        "Allianz pollution",
        "Allianz fossil fuel",
        "Allianz incident",
    ]
    date_index = get_query_date_index()

    # df_zeros = pd.DataFrame(np.zeros((query_length*len(keywords), 3)), columns=['date','keyword', 'search_interest'])
    # df_zeros['keyword'] = np.repeat(keywords, query_length)

    # # set date for each keyword
    # df_zeros['date'] = pd.concat([date_index for i in range(len(keywords))], axis=0, ignore_index=True)

    # print(df_zeros.query("keyword == 'adidas manipulation'").head().to_markdown())
    # print(df_zeros.query("keyword == 'adidas manipulation'").tail().to_markdown())

    # print(df_zeros.query("keyword == 'adidas dispute'").head().to_markdown())
    # print(df_zeros.query("keyword == 'adidas dispute'").tail().to_markdown())

    # print(df_zeros.query("keyword == 'Allianz fossil fuel'").head().to_markdown())
    # print(df_zeros.query("keyword == 'Allianz fossil fuel'").tail().to_markdown())

    print(f"Date index: {date_index.head().to_markdown()}")
    # create empty df with 0s
    query_length = len(date_index)
    # init dataframe with 0
    df_zeros = pd.DataFrame(
        np.zeros((query_length * len(keywords), 3)),
        columns=["date", "keyword", "search_interest"],
    )
    # replace 0s with keywords
    df_zeros["keyword"] = np.repeat(keywords, query_length)
    # replace 0s with dates
    df_zeros["date"] = pd.concat([date_index for i in range(len(keywords))], axis=0, ignore_index=True)
