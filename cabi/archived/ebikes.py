### DEPRECATE THESE? OLD VERSIONS OF CLEANING FUNCTIONS FOR JUST EBIKES
### NO LONGER WORKING WITH THESE


import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
from cabi.utils import which_anc, station_anc_dict
from cabi.get_data import anc_gdf

gdf = anc_gdf()
anc_dict = station_anc_dict()
station_keys = anc_dict.keys()




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

def load_clean_full():
    """DOCSTRING MAKE THIS EXTENSIBLE TO MORE MONTHS"""
    df = pd.read_pickle('../data/wip/raw_apr_to_jul_df.pkl')
    cleaned_full = clean_frame(df)
    return cleaned_full

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
