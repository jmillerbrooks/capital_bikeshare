import requests
import zipfile
import io
import itertools
import datetime as dt
import os
import shutil
import pandas as pd
import geopandas as gpd

### Section One Download and Extract the raw zipfiles of trip data ###


# Build list of months in the format of the url/csv filepaths provided
# by CABI
def build_months():
    """DOCSTRING"""
    months = [f'0{i}' if i in range(1,10) else f'{i}' for i in range(1,13)]
    return months

# Get current date for cleaner build_paths function
today = dt.date.today()

# Build url/csv filepaths COME BACK TO THIS, JUST POPULATED WITH DEFAULTS FOR NOW NEEDS SOME CONDITIONALS
def build_paths(start_month=1, end_month=today.month - 2, end_year=today.year, start_year=2018, csv_url='zip'):
    """DOCSTRING accepts zip or csv start/end year months etc. ADD TRY EXCEPT this will also break if we are towards the
    start of a new year, etc.
    
    Current version will only return paths for last two years 2018, 2019, and current year 2020 through July"""
    # build range of years to pull
    year_range = range(start_year, end_year + 1)
    months = build_months()
    
    if csv_url == 'zip':
        paths_2018 = [f'https://s3.amazonaws.com/capitalbikeshare-data/2018{month}-capitalbikeshare-tripdata.{csv_url}' for month in months]
        paths_2019 = [f'https://s3.amazonaws.com/capitalbikeshare-data/2019{month}-capitalbikeshare-tripdata.{csv_url}' for month in months]
        paths_2020 = [f'https://s3.amazonaws.com/capitalbikeshare-data/2020{month}-capitalbikeshare-tripdata.{csv_url}' for month in months[0:7]]
    # if csv_url equals csv
    else:
        paths_2018 = [f'../data/raw/2018{month}-capitalbikeshare-tripdata.{csv_url}' for month in months]
        paths_2019 = [f'../data/raw/2019{month}-capitalbikeshare-tripdata.{csv_url}' for month in months]
        paths_2020 = [f'../data/raw/2020{month}-capitalbikeshare-tripdata.{csv_url}' for month in months[0:7]]
    return paths_2018, paths_2019, paths_2020
    
    
def get_zip(path):
    """Downloads zipfile containing csv of monthly capital bikeshare trip data and unzips
    contents in the ~/data/raw folder """
    r = requests.get(path)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall('../data/raw/')
    pass


def get_zips(*args):
    """Calls get_zip on an iterable of url paths corresponding to locations of
    Capital Bikeshare zipfiles containing csvs of monthly trip data
    No Return value in notebook, but populates ~/data/raw with the unzipped csv files"""
    # Combines all iterables passed as *args into generator that generates 1 iterable
    paths = itertools.chain(*args)
    # Applies the get_zip function to each path in the above generated iterable and
    # unpacks the resulting generator to execute each, downloading zip file from source
    # given in path and unzipping into csv format in the data/raw directory
    [*map(get_zip, paths)]
    pass

## GET RID OF THIS WHEN MAKE SETUP.PY
def make_raw_dir():
    """DOCSTRING"""
    os.mkdir('../data/')
    os.mkdir('../data/raw/')
    pass

def clean_dir(dir_path='../data/raw/'):
    """Remove the _MACOSX output and fix filenames as necessary"""
    # Files/dirs to remove
    try:
        mac_crap = dir_path + '__MACOSX/'
        # Remove the __MACOSX/ subdirectory
        shutil.rmtree(mac_crap)
    except:
        pass
    # Remove .DS_store
    try:
        ds_store = dir_path + '.DS_Store'
        os.remove(ds_store)
    except:
        pass
    
    # Replace files not ending with csv with csv
    files = os.listdir(dir_path)
    to_replace = [dir_path + file for file in files if not file.endswith('.csv')]
    for file in to_replace:
        cleaned = file + '.csv'
        os.rename(file, cleaned)
    
    # Renames a small number of csv files not formatted like the others in consistent format
    to_format = [dir_path + file for file in files if '_' in file]
    for file in to_format:
        if 'ipynb' not in file:
            formatted = to_format[0].replace('_', '-')
            os.rename(file, formatted)
    pass
    

def build_raw_data():
    """Calls make_raw_dir to create ~/data/raw, build_paths to define url locations of zipped czv files
    and get_zips on the resulting url paths to download the files to ~/data/raw and unzip them to csv.
    Finally calls clean_dir to remove any unwanted outputs from the ~/data/raw directory, and prints the
    names of the new files in the new directory.
    No return output in notebook"""
    
    # Remove after building setup.py?
    make_raw_dir()
    
    # Fix this to make extensible to different ranges
    p1, p2, p3 = build_paths()
    
    get_zips(p1, p2, p3)
    
    clean_dir()
    files = os.listdir('../data/raw')
    print(f'created directory ~/data/raw with contents: /n{files}')
    pass


def compile_paths(*args):
    """accepts n lists, returns 1 list"""
    # Chain creates generator of iterables passed in args combined into one iterable
    # this is unpacked into the list paths and returned as output
    paths = [*itertools.chain(*args)]
    return paths


def import_csvs(csv_paths):
    """Accepts a list of csv_paths from data/raw/
    Returns a list of DataFrames from these paths"""
    raw_dfs = [*map(pd.read_csv, csv_paths)]
    return raw_dfs


def dfs_from_raw():
    """Read the csv files that make up the contents of ~/data/raw
    into a list of pandas dataframes, returns a list of dataframes"""
    # Lists of filenames generated from build_raw_data
    a, b, c = build_paths(csv_url='csv')

    # compile filenames into a single list
    csv_paths = compile_paths(a,b,c)
    
    # Build a list of dataframes generated by each csv in the data/raw directory
    raw_dfs = import_csvs(csv_paths)
    
    return raw_dfs


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
    # Downloads DC Boundary JSON from Open Data DC
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
    """Retrieves basic information on the capital bikeshare stations from public API,
    Returns the results as a pandas dataframe with columns ['name', 'region_id', 'lat', 'lon'] """
    stations_info_response = requests.get('https://gbfs.capitalbikeshare.com/gbfs/en/station_information.json')
    stations_info = stations_info_response.json()
    stations_info_df = pd.DataFrame(stations_info['data']['stations'])
    stations_info_df = stations_info_df[['name', 'region_id', 'lat', 'lon']]
    return stations_info_df
