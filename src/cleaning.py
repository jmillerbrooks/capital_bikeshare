import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
from src.utils import which_anc, station_anc_dict
from src.get_data import anc_gdf

gdf = anc_gdf()
anc_dict = station_anc_dict()
station_keys = anc_dict.keys()

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
        coord = row.start_coord
    else:
        station = row.end_station_name
        coord = row.end_coord
    
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

def rename_columns(df, legacy=False):
    """DOCSTRING
    build out legacy=True to rename the columns of the old version of the data
    """
    df = df.rename(
        columns={
            'started_at':'time-start',
            'ended_at':'time-end',
            'start_station_name':'station_name-start',
            'end_station_name':'station_name-end'
        })
    return df

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
    
    df = to_geo(df)
    
    
    
    # Convert all datetimes to datetime format
    df['started_at'] = pd.to_datetime(df.started_at)
    df['ended_at'] = pd.to_datetime(df.ended_at)
    
    # Engineer some additional features such as start/end hour of day, day of week and duration
#     df['started_hour'] = df.started_at.dt.hour
#     df['ended_hour'] = df.ended_at.dt.hour
#     df['day_of_week'] = df.started_at.dt.day_name()
    df['duration'] = df.ended_at - df.started_at
    df['duration_seconds'] = df.duration.dt.total_seconds()


    
    # Drop duration, and ride_id columns.
    # We have duration seconds, ride_id is not particularly useful 
    # since we are interested in aggregate numbers instead of individual trips
    # DEBUGGING INCLUDING (, 'ride_id')
    cleaned_df = df.drop(['duration'], axis=1)
    
    

    
    # Remove trips that last longer than 15 hours (outliers)
    cleaned_df = cleaned_df.loc[cleaned_df.duration_seconds < 60*60*15]
    # Remove trips with negative duration
    cleaned_df = cleaned_df.loc[cleaned_df.duration_seconds > 0]

    # Remove start_station_id and end_station_id, this information is duplicated in station name cols, as well as lng/lat combination
    cleaned_df = cleaned_df.drop(['start_station_id', 'end_station_id'], axis=1)
    
    cleaned_df = rename_cols(cleaned_df)
    
    # Return the cleaned df
    return cleaned_df



def load_clean_full():
    """DOCSTRING MAKE THIS EXTENSIBLE TO MORE MONTHS"""
    df = pd.read_pickle('../data/wip/raw_apr_to_jul_df.pkl')
    cleaned_full = clean_frame(df)
    return cleaned_full

def rename_cols(df):
    """Prepare Column Names for wide_to_long operation below"""
    renamed = df.rename(
        columns={'started_at':'time-start',
                 'ended_at':'time-end',
                 'ANC_start':'ANC-start',
                 'ANC_end':'ANC-end',
                 'geom_start':'coord-start',
                 'geom_end':'coord-end',
                 'start_station_name':'station_name-start',
                 'end_station_name':'station_name-end'
                })
    return renamed


def long_ts_geo(df):
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
        full_import,
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
    return gpd.GeoDataFrame(rides_long_ts)

def net_gain_loss(location, df, col='ANC'):
    """Return an np.array of the effect of ride on a given column value's net gain or loss in 1 0 -1 VALUES
    1 if RIDE ENDED IN location 0 IF RIDE DID NOT LEAVE OR END IN location -1 IF RIDE LEFT FROM location
    will be the length of the df/col passed as params"""
    
    conditions = [
        (df['start_end'] == 'start') & (df[col] == location),
        (df['start_end'] == 'end') & (df[col] == location),
        (df[col] != location)
        ]

    values = [
        -1,
        1,
        0
    ]
    
    return np.select(conditions, values)


### Figure out how computationally expensive it would be to store all results including the exogenous columns
def plus_minus_locations(df, col='ANC'):
    """DOCSTRING, accepts a location column, returns a df where the columns correspond to
    the values of the col passed in params, values of each column are a timeseries of gain/loss
    values one of (-1,0,1) yielded from net_gain_loss_location"""
    
    # Build iterable of locations from unique values of a column, ignoring entries that are not in an ANC
    # This is an area for future improvement, see for example map of rides that did not end in ANC but started
    # Outside of DC, there is a clear edge effect, indicating that a better approach here would be to cluster
    # locations throught the entire region rather than using the rather arbitrary ANC tiling
    # used here for expediency to limit scope of the project
    locations = locations = [location for location in df[col].unique() if location != 'Outside']
    
    # Create dictionary of locations (keys) and series of plus minus values returned
    # from net_gain_loss(location, df, col=col) for each unique location in locations
    plus_minus_dict = {location: net_gain_loss(location, df, col) \
                       for location in \
                       locations}
    # Convert dict to dataframe, index by the (time) index of long_anc_df passed
    plus_minus_df = pd.DataFrame(plus_minus_dict, index=df.index)
    
    return plus_minus_df


def cumulative_change(df, window_size):
    """DOCSTRING window_size must be an int or offset passable to pandas.DataFrame.rolling(window)
    intended for use as an offset"""
    rolling_df = pd.concat([ \
                            df[col].rolling(window_size) \
                            .sum() \
                            for col in df.columns] \
                           , axis=1)
    return rolling_df
    
    

    
### DEPRECATE THESE? MOVE TO A DIFFERENT MODULE?

## NEEDS WORK!! FIX GET_DATA MODULE SO THAT LOAD CLEAN DOCKLESS CAN JUST CALL FROM THERE
def load_clean_dockless():
    # FIX THIS CALL GET_DATA MODULE
    df = pd.read_pickle('../data/wip/raw_dockless.pkl')
    cleaned_ebikes = clean_frame(df)
    cleaned_ebikes = cleaned_ebikes.drop('rideable_type', axis=1)
    return cleaned_ebikes

    
    
def load_geo_ebikes():
    df = load_clean_dockless()
    geo_ebikes = to_geo(df)
    return geo_ebikes

def geo_longer(df):
    """NEEDS DOCSTRING THIS FUNCTION MAKES ONE TIME COLUMN FROM START/END
    AND DOUBLES THE LENGTH OF THE DF IN PROCESS, A GOOD TEST IS WHETHER OR NOT
    THE LEN IS 2x OG DF"""
    # List all the columns that are not start/end time for easy melt operation below
    cols = list(df.columns)
    cols.remove('started_at')
    cols.remove('ended_at')

    # Combine started_at/ended_at into one column 'time', indicating whether
    # this was a trip start or trip end in another column, 'start_end', 
    # set index of new df to 'time'
    # sort the index, so it makes sense as a time series
    long_geo = df.rename(columns={'started_at': 'start', 'ended_at': 'end'}) \
        .melt(id_vars=cols \
              , value_vars=['start', 'end'] \
              , var_name='start_end' \
              , value_name='time') \
        .set_index('time') \
        .sort_index()
    return long_geo

def load_long_geo():
    """DOCSTRING"""
    df = load_geo_ebikes()
    long_geo = geo_longer(df)
    return long_geo

def load_long_geo_full():
    """DOCSTRING"""
    df = load_geo_ebikes()
    long_geo = geo_longer(df)
    return long_geo

def anc_frame(df):
    """DOCSTRING"""
    
    anc_df = df.drop(['start_station_name', 'end_station_name'], axis=1)
    return anc_df

def load_long_anc():
    """DOCSTRING"""
    df = load_long_geo()
    anc_df = anc_frame(df)
    return anc_df


# NEEDS WORK!! FIX DOCSTRING!! GENERALIZE TO ANY LOCATION COL (station etc.) 
# This is likely uneccesary now that we have a more generalized long df function
def net_gain_loss_anc(ANC_name, df):
    """NEEDS DOCSTRING THIS FUNCTION RETURNS A SERIES (list? np.array?) OF 1 0 -1 VALUES
    1 if RIDE ENDED IN ANC 0 IF RIDE DID NOT LEAVE OR END IN ANC -1 IF RIDE LEFT FROM ANC"""
    
    conditions = [
        (df['start_end'] == 'start') & (df['ANC_start'] == ANC_name),
        (df['start_end'] == 'end') & (df['ANC_end'] == ANC_name),
        (df['ANC_start'] != ANC_name) & (df['ANC_end'] != ANC_name),
        (df['start_end'] == 'end') & (df['ANC_end'] != ANC_name),
        (df['start_end'] == 'start') & (df['ANC_start'] != ANC_name)
        ]

    values = [
        -1,
        1,
        0,
        0,
        0
    ]
    
    return np.select(conditions, values)

def plus_minus_anc_frame(df):
    """DOCSTRING GENERALIZE THIS FUNCTION TO ACCEPT OTHER THINGS BESIDE ANC REMOVE DEPENDENCY ON GDF"""
    
    
    # Create dictionary of ancs (keys) and series of plus minus values returned from net_gain_loss_anc (values)
    # for each unique ANC_ID
    plus_minus_dict = {anc: net_gain_loss_anc(anc, df) \
                       for anc in \
                       list(gdf.ANC_ID)}
    # Convert dict to dataframe, index by the (time) index of long_anc_df passed
    anc_plus_minus_df = pd.DataFrame(plus_minus_dict, index=df.index)
    
    return anc_plus_minus_df

def load_plus_minus_anc():
    df = load_long_anc()
    plus_minus = plus_minus_anc_frame(df)
    return plus_minus



    
    

