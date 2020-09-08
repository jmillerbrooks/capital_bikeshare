import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
from cabi.geometry import point_series, anc_from_dict, which_anc

## To Check Join Compatibility of raw dfs
def check_col_names(df1, df2, cols_only=True):
    """Return True or False indicating whether or not the column names are the same between two dataframes"""
    # Default is that columns are passed, for ease of use
    # with check_col_list below
    # will return truth value for each column pair, so we achieve
    # one truth value for the whole array/list by calling all
    if cols_only:
        result = all(df1 == df2)
    # Also possible to pass two dataframes directly by specifying
    # cols_only=False
    else:
        result = all(df1.columns == df2.columns)
    # Return True/False result
    return result

def check_col_list(df_list):
    """Accepts list of dataframes, calls check_col_names on the df columns
    returns False if any False values, true otherwise"""
    
    # Build dict of df columns keyed by position in list
    # Only pull the columns to save some space
    # Save as dict to make returning the mismatches easier on
    # later edit
    col_dict = {i: df.columns for i, df in enumerate(df_list)}
    
    # build list of keys for cleaner reading below
    keys = list(col_dict.keys())
    
    
    # Because we are only interested in if there are any False values
    # we can compare one df to all others by the logic that if a==b,
    # a==c, a==d, etc. then a==b==c==d and so on
    results = [check_col_names(col_dict[0], col_dict[key]) for key in keys]
    
    # return True only if all are true
    
    return all(results)

def drop_legacy_cols(df):
    """Accepts df in raw format from prior to April of 2020
    Returns same df without the columns ['Duration', 'Start station number', 
    'End station number', 'Bike number'] Duration is created later in
    cleaning process to ensure consistent results Station Number cols
    duplicate information in station name cols and are of different 
    format to current numbering scheme, bike number is unavailable in
    current datasets"""
    return df.drop(['Duration', 'Start station number', 'End station number', 'Bike number'], axis=1)


def rename_legacy_cols(df):
    """Renames columns of dataframe in format consistent with the current naming scheme"""
    return df.rename(
        columns={'Start date':'started_at',
                 'End date': 'ended_at',
                 'Start station':'start_station_name',
                 'End station': 'end_station_name',
                 'Member type': 'member_casual'}
    )

def legacy_to_recent(df):
    """Returns df formatted in the same style as employed from April of 2020
    by calling drop/rename legacy cols funcs in succession, adding a rideable_type
    and correcting type-case of the member_casual column 
    """
    new_df = drop_legacy_cols(df)
    new_df = rename_legacy_cols(new_df)
    # impute rideable type since ebikes were not rolled out until after
    # any of these data sets were released
    new_df['rideable_type'] = 'docked_bike'
    # convert values to lower case
    new_df['member_casual'] = new_df.member_casual.str.lower()
    
    return new_df

def join_legacy(df_list):
    """Returns one DataFrame in current format from list of legacy
    formatted dataframes"""
    # format each dataframe in the list, combine them into one new dataframe with a new index
    full = pd.concat([legacy_to_recent(df) for df in df_list], ignore_index=True)
    # Allowing us to keep the ride_id column for the newer dataframes since none of the existing
    # ride ids are integers
    full['ride_id'] = pd.Series(range(len(full)))
    # The columns are slightly out of order, since we defined a new column 'rideable_type'
    # with our legacy_to_recent function which is the second column in the new format.
    # and then defined a ride_id which is the first. We first reorder the columns:
    cols = [col for col in full.columns]
    cols = [cols[-1], cols[-2]] + cols[:-2]
    # And then reindex the new dataframe
    full = full[cols]
    
    return full

def drop_recent_cols(df):
    """Accepts a dataframe from April of 2020 or later
    Returns dataframe suitable for a temporary join with historical data
    to demonstrate decisions made in EDA process as discussed in Technical
    Notebook"""
    return df.drop(['start_station_id', 'end_station_id', 'start_lat', 'start_lng', 'end_lat', 'end_lng'], axis=1)

def drop_equity(df):
    """This column appears in only one dataframe and is no longer reported"""
    if 'is_equity' in df.columns:
        result = df.drop('is_equity', axis=1)
    else:
        result = df
    
    return result


def join_recent(df_list):
    new_list = [drop_equity(df) for df in df_list]
    return pd.concat([drop_recent_cols(df) for df in new_list], ignore_index=True)

def clean_merged(df):
    """Quick wrapper to allow datetime operations during EDA"""
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['ended_at'] = pd.to_datetime(df['ended_at'])
    merged_df = df.set_index('started_at')
    merged_df = merged_df.sort_index()
    return merged_df

def merge_all(legacy_df_list, recent_df_list):
    temp = pd.concat([join_legacy(legacy_df_list), join_recent(recent_df_list)], ignore_index=True)
    return clean_merged(temp)

    


## Ugly dude. Ugly. Split this up.
def clean_frame(df):
    """Perform a number of cleaning operations on the dockless ebikes data. Return clean df.
    
    Params: (df) a pandas DataFrame of trip data on dockless ebikes from Capital Bikeshare
    
    Returns: (df) a cleaned pandas DataFrame of trip data on dockless ebikes from Capital Bikeshare"""
    
    
    # Remove trips that have missing lat/lng coords briefly considered imputation
    # but the fact that all of these are missing station values as well
    # makes a strong case for this just being bad data
    df = df.loc[~(df.start_lat.isna() | df.start_lng.isna())]
    df = df.loc[~(df.end_lat.isna()| df.end_lng.isna())]
    
    # Variable to hold the location of the CaBi warehouse, these trips should not be included in analysis
    # as they are presumably maintenance related and many of them are the terminus of extremely 
    # long trips suggesting recovered bikes being taken out of circulation
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
    
    


    
    

    



    
    

