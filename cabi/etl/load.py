"""
Load Module Interacts with PostGIS/Postgresql databases in this project
Includes functions for loading data from the existing DB with sql queries
once built as well as loading transformed data into tables in the CABI db.

This might belong in same place as model or main, since it is for the
moment only pulling from rather than writing to.
"""


import pandas as pd
import geopandas as gpd
import sqlalchemy
from geoalchemy2 import Geometry, WKTElement
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

def load_counts_full():
    """DOCSTRING
    Load the whole counts db into a df
    """
    
    
    engine = sqlalchemy.create_engine(conn)
    
    query = f"""
    SELECT *
    FROM plus_minus
    """
    
    df = gpd.read_postgis(
        query,
        engine,
        parse_dates='time'
    ).set_index(
        'time'
    )
    
    # Ensure db connections are closed
    engine.dispose()
    
    return df


def load_trips():
    """Read the trips_long table into a pandas dataframe 
    from the postgis db created in ETL phase"""
    
    engine = sqlalchemy.create_engine(conn)
    
    connection = engine.connect()
    query = f"""
    SELECT * 
    FROM trips_long
    """

    df = gpd.read_sql(
        query,
        connection,
        geom_col='geom_coord',
        parse_dates='time'
    ).set_index(
        'time'
    )

    # Ensure db connections are closed
    engine.dispose()
    
    return df

def write_postgis(df, table_name='trips_long'):
    """Create or append to existing sql table in our database 
    the results of transformed df"""
    
    # Create a sql engine with the params user specifies in config.py
    # to use in connecting to the database we will be writing to
    engine = sqlalchemy.create_engine(conn)
    
    # make a copy of the dataframe to write
    geodataframe = df.copy()
    
    # create a new column to hold coordinate geometries in postgis format
    # this applies WKTElement to each coordinate in our existing coord column
    # to convert from the existing shapely Point objects that geopandas
    # interacts with to postgis readable points
    geodataframe['geom_coord'] = geodataframe['coord'].apply(lambda x: WKTElement(x.wkt, srid=4326))



    #drop the coord column so we don't write twice
    geodataframe.drop('coord', axis=1, inplace=True)


    geodataframe.to_sql(
        table_name, # specify table name for the table to write to from params
        engine, # specify engine to use for connecting to the db
        if_exists='append', # if table exists append nedw values to the existing table
        index=True, # write our time index as a column
        index_label='time', # keep column name for the above line in the new table
        # Use 'dtype' to specify column's type for postgis
        # For the geom column, we will use GeoAlchemy's type 'Geometry'
        # as discussed above since it is compatible with postgis
        dtype={
            'geom_coord': Geometry(
                geometry_type='POINT', # write as point objects
                srid=4326) # the spatial reference identifier for the coordinate system used in this set
        })
    
    # Ensure db connections are closed
    engine.dispose()
    
    pass

def write_postgres(df, table_name='plus_minus'):
    """Simple wrapper around a sql query to use where no additional transformation
    of data formats is necessary to fit into new target table
    Creates a postrgresql table (by default named 'plus_minus') in the CABI database
    from a pandas DataFrame by calling to_sql with the sqlalchemy
    engine created from the user supplied information in config.py"""
    
    # Create a sql engine with the params user specifies in config.py
    # to use in connecting to the database we will be writing to
    engine = sqlalchemy.create_engine(conn)
    
    # Call pandas to_sql method passing the table name and engine
    # use append as described above in write_postgis
    # Pass index to ensure it's written as a column
    # giving column name 'time' note, it is recommended 
    # that the user not utilize chunksize on either read or write
    # unless they have detailed knowledge of how it works, as it 
    # will be much easier to maintain the order of the records
    # without it. Further approaches to timeseries indexing
    # in sql were outside of the scope of this project, but numerous
    # resources are available with a quick google search if the user
    # is curious
    df.to_sql(
    table_name,
    engine,
    if_exists='append',
    index=True,
    index_label='time'
    )
    
    # Ensure db connections are closed
    engine.dispose()
    
    pass