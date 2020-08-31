import requests
import zipfile
import io
import itertools
import datetime as dt
import os
import shutil
import pandas as pd

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
    """DOCSTRING"""
    r = requests.get(path)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall('../data/raw/')
    pass


def get_zips(*args):
    """DOCSTRING"""
    paths = itertools.chain(*args)
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
    
    to_format = [dir_path + file for file in files if '_' in file]
    for file in to_format:
        if 'ipynb' not in file:
            formatted = to_format[0].replace('_', '-')
            os.rename(file, formatted)
    pass
    

def build_raw_data():
    """DOCSTRING"""
    
    # Remove after building setup.py
    make_raw_dir()
    
    # Fix this to make extensible to different ranges
    p1, p2, p3 = build_paths()
    
    get_zips(p1, p2, p3)
    
    clean_dir()
    pass

def compile_paths(*args):
    """accepts n lists, returns 1 list"""
    paths = [*itertools.chain(*args)]
    return paths





def import_csvs(csv_paths):
    """Accepts a list of csv_paths from data/raw/
    Returns a list of DataFrames from these paths"""
    raw_dfs = [*map(pd.read_csv, csv_paths)]
    return raw_dfs

# def 