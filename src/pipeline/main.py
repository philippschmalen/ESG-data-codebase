import prefect
from prefect import task, Parameter, Flow

from src.data.gtrends_extract import (
    create_pytrends_session,
    get_related_queries,
    process_related_query_response,
    unpack_related_queries_response,
    create_related_queries_dataframe,
)
