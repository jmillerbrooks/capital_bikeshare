import requests
import zipfile
import io
import itertools
import pandas as pd
import geopandas as gpd
import json



def formatted_months():
    # Generate list of months of year formatted as in zipped files urlnames/resulting csv pathnames
    months = [f'0{i}' if i in range(1,10) else f'{i}' for i in range(1,13)]
    return months

## NEEDS WORK!!
def url_paths(start_year=2018, end_year=2020, start_month=0, end_month=7):
    # call formatted_months func to build list of months formatted as in the url paths from CABI website
    months = formatted_months()
    # Lists of download urls
    
    paths_2018 = [f'https://s3.amazonaws.com/capitalbikeshare-data/2018{i}-capitalbikeshare-tripdata.zip' for i in months]
    paths_2019 = [f'https://s3.amazonaws.com/capitalbikeshare-data/2019{i}-capitalbikeshare-tripdata.zip' for i in months]
    # Only generate paths for the months 
    paths_2020 = [f'https://s3.amazonaws.com/capitalbikeshare-data/2020{i}-capitalbikeshare-tripdata.zip' for i in months[start_month:end_month]]
    pass
    



def get_zip(path):
    """Download and extract contents of zipfile from given url.
    
    Args:
        path (str): url location of zipped file.
    
    Returns:
        extracted contents of zipfile in the directory '../data/raw/'
    
    """
    r = requests.get(path)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return z.extractall('../data/raw/')

def get_zips(*args):
    """Calls get_zip on an iterable of url paths.
    
    Args:
        *args (iterable): iterable or iterables of url paths
        
    Returns:
        list of Nonetype, extracted contents of all zipfiles specified by the urls in *args"""
    # Make one iterable from the *args
    paths = itertools.chain(*args)
    # Unpack map object, returning None in console and unzipped contents of each url in ../data/raw
    return [*map(get_zip, paths)]

## NEEDS WORK!!!!
def read_dfs():
    """Return a list of dataframes of trip data corresponding to the months passed in the months param
    
    Params: months (list) a list of months formatted in the style of 
    
    Returns: (list) a list of dataframes of trip data corresponding to the months passed in months Param"""
    
    months = formatted_months()
    
    pass
    
# Data for various geometries

def load_ancs():
    # Downloads ANC JSON from Open Data DC
    url = "https://opendata.arcgis.com/datasets/fcfbf29074e549d8aff9b9c708179291_1.geojson"
    response = requests.get(url)
    content = response.json()
    return content

def anc_gdf():
    """Return a GeoDataFrame of DC ANC geometries (Advisory Neighborhood Commissions)"""
    anc_json = load_ancs()
    anc_gdf = gpd.GeoDataFrame.from_features(anc_json["features"])
    return anc_gdf

def load_dc_boundary():
    # Downloads ANC JSON from Open Data DC
    url = "https://opendata.arcgis.com/datasets/7241f6d500b44288ad983f0942b39663_10.geojson"
    response = requests.get(url).json()
    return response
    
def dc_polygon():
    """Return a GeoDataFrame of DC ANC geometries (Advisory Neighborhood Commissions)"""
    dc_json = load_dc_boundary()
    gdf = gpd.GeoDataFrame.from_features(dc_json["features"])
    return gdf.geometry[0]

def load_outside_regions():
    """returns a list of region ids corresponding to regions not in DC
    can be used to quickly subset stations not in DC, to avoid more expensive
    geographic lookup computations"""
    system_regions_response = requests.get('https://gbfs.capitalbikeshare.com/gbfs/en/system_regions.json')
    system_regions = system_regions_response.json()
    regions_df = pd.DataFrame(system_regions['data']['regions'])#.region_id
    outside_regions = regions_df.loc[\
                                     ~regions_df.region_id
                                     .isin(['42', '128', '48'])
                                     , 'region_id']
    return list(outside_regions.values)
    
def load_station_info():
    """DOCSTRING"""
    stations_info_response = requests.get('https://gbfs.capitalbikeshare.com/gbfs/en/station_information.json')
    stations_info = stations_info_response.json()
    stations_info_df = pd.DataFrame(stations_info['data']['stations'])
    stations_info_df = stations_info_df[['name', 'region_id', 'lat', 'lon']]
    return stations_info_df
    
    

