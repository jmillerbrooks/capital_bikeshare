import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
from cabi.utils import which_anc, station_anc_dict
from cabi.etl.get_data import anc_gdf

gdf = anc_gdf()
anc_dict = station_anc_dict()
station_keys = anc_dict.keys()

##Ugly dude. Ugly. Split this up.
def clean_frame(df):
    """Perform a number of cleaning operations on the dockless ebikes data. Return clean df.
    
    Params: (df) a pandas DataFrame of trip data on dockless ebikes from Capital Bikeshare
    
    Returns: (df) a cleaned pandas DataFrame of trip data on dockless ebikes from Capital Bikeshare"""
    
    
    # Remove trips that have missing lat/lng coords
    df = df.loc[~(df.start_lat.isna() | df.start_lng.isna())]
    df = df.loc[~(df.end_lat.isna()| df.end_lng.isna())]
    
    # Variable to hold the location of the warehouse, these trips should not be included in analysis
    warehouse = '6035 Warehouse'
    
    # Remove trips that end at the warehouse
    df = df.loc[df.end_station_name != warehouse]
    
    # Convert all datetimes to datetime format
    df['started_at'] = pd.to_datetime(df.started_at)
    df['ended_at'] = pd.to_datetime(df.ended_at)
    
    # Add duration_seconds column
    df['duration'] = df.ended_at - df.started_at
    df['duration_seconds'] = df.duration.dt.total_seconds()

    cleaned_df = df.drop(['duration'], axis=1)
    

    # Remove trips that last longer than 15 hours (outliers)
    cleaned_df = cleaned_df.loc[cleaned_df.duration_seconds < 60*60*15]
    # Remove trips with negative duration
    cleaned_df = cleaned_df.loc[cleaned_df.duration_seconds > 0]

    # Remove start_station_id and end_station_id, this information is duplicated in station name cols, as well as lng/lat combination
    cleaned_df = cleaned_df.drop(['start_station_id', 'end_station_id'], axis=1)
    
    
    # Return the cleaned df
    return cleaned_df

def point_series(lng_col, lat_col, name, index_col):
    """Takes 2 pandas series (don't pass a df) and returns a GeoSeries of shapely POINT objects, indexed by index_col"""
    # Zip lng/lat together, and make a point out of each 
    points = gpd.GeoSeries([Point(lng, lat) for lng, lat in zip(lng_col, lat_col)] \
                           , name=name \
                           , index=index_col)
    return points

def anc_from_dict(station):
    """DOCSTRING"""
    # For each observation in a df, if there exists a station
    # pull the ANC from station_dict
    if station in station_keys:
        result = anc_dict[station]
    else:
        result = None
    
    return result

def apply_anc(row, side='start'):
    """DOCSTRING"""
    if side == 'start':
        station = row.start_station_name
        coord = row['coord-start']
    else:
        station = row.end_station_name
        coord = row['coord-end']
    
    lookup = anc_from_dict(station)
    if lookup:
        result = lookup
    else:
        result = which_anc(coord)
        
    return result
    
def anc_cols(df):
    """DOCSTRING"""    
    # Create 'ANC_start' column with the 
    df['ANC-start'] = df.apply(lambda x: apply_anc(x, side='start'), axis=1)

    # Create 'ANC_end' column with the 
    df['ANC-end'] = df.apply(lambda x: apply_anc(x, side='end'), axis=1)
    return df


def rename_columns(df, legacy=False):
    """DOCSTRING
    build out legacy=True to rename the columns of the old version of the data
    Prepares columns for the wide-to-long function
    """
    df = df.rename(
        columns={
            'started_at':'time-start',
            'ended_at':'time-end',
            'start_station_name':'station_name-start',
            'end_station_name':'station_name-end'
        })
    return df


def to_geo(df, ANC=True):
    """Custom function to transform cleaned_ebikes into GeoDataFrame"""
    
    
    # Call point series on start_lng/start_lat to generate a GeoSeries of start_points indexed by started_at
    start_points = point_series(lng_col=df['start_lng'] \
                                , lat_col=df['start_lat'] \
                                , name='coord-start' \
                                , index_col=df['ride_id'])
    
    # Call point series on end_lng/end_lat to generate a GeoSeries of end_points indexed by started_at
    end_points = point_series(lng_col=df['end_lng'] \
                              , lat_col=df['end_lat'] \
                              , name='coord-end' \
                              , index_col=df['ride_id'])
    
    # Merge start/endpoints with df (cleaned_ebikes), drop original lat/lng columns
    geo_ebikes = df.merge(start_points, on='ride_id') \
    .merge(end_points, on='ride_id') \
    .drop(['start_lat', 'start_lng', \
          'end_lat', 'end_lng'], axis=1)
    
    if ANC == True:
        geo_ebikes = anc_cols(geo_ebikes)
    else:
        pass
    
    
    # Convert to GeoDataFrame for easier spatial operations, set default geometry to the start_coord column
    geo_ebikes = gpd.GeoDataFrame(geo_ebikes, geometry='coord-start')
    
    return geo_ebikes


def to_long(df):
    """DOCSTRING making the long family more general
    returns long format version of geodataframe indexed
    by time"""
    
    # Melt Data to long format, including a start/end indicator
    # for each ride, essentially a dataframe of checkins/checkouts
    # instead of full rides. Duration column remains as 
    # potentially useful target for some models 
    # (so do all other columns not prefixed with an
    # element appearing in stubnames)
    rides_long = pd.wide_to_long(
        df,
        stubnames=['time', 'ANC', 'station_name', 'coord'],
        i='ride_id',
        j='start_end',
        sep='-',
        suffix='\w+')

    # Set index to a timeseries and sort
    rides_long_ts = rides_long\
        .reset_index()\
        .set_index('time')\
        .sort_index()
    
    # Return GeoDataFrame version
    return gpd.GeoDataFrame(rides_long_ts, geometry='coord')

def full_transform(df):
    """DOCSTRING
    Accepts Raw Data from (FOR RIGHT NOW JUST APR to JUL)
    Returns Long Format Data to Load into POSTGIS db"""
    transformed = clean_frame(df)
    transformed = to_geo(transformed)
    transformed = rename_columns(transformed)
    long = to_long(transformed)
    return long
    
    


    
    

    



    
    

