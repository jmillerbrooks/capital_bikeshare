"""
Load Module Interacts with PostGIS/Postgresql databases in this project
Includes functions for loading data from the existing DB with sql queries
once built as well as loading transformed data into tables in the CABI db.
"""


import pandas as pd
import geopandas as gpd
import sqlalchemy
import cabi.etl.config as config

conn = config.connection_params()

def load_counts(col):
    """Accepts a column name present in postgres db of timeseries
    Returns the column as a pandas series indexed by time"""
    
    engine = sqlalchemy.create_engine(conn)
    
    query = f"""
    SELECT time, "{col}"
    FROM plus_minus
    """

    series = pd.read_sql(
        query,
        engine,
        parse_dates='time'
    ).set_index(
        'time'
    )

    # Ensure db connections are closed
    engine.dispose()
    
    return series[col]
