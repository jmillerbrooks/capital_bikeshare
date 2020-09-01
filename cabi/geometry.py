from functools import partial, lru_cache, wraps
import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point
from cabi.etl.get_data import anc_gdf, dc_polygon, load_station_info, load_outside_regions



gdf = anc_gdf()
stations_df = load_station_info()
outside_regions = load_outside_regions()
dc_boundary = dc_polygon()


def point_series(lng_col, lat_col, name, index_col):
    """Takes 2 pandas series (don't pass a df) and returns a GeoSeries of shapely POINT objects, indexed by index_col"""
    # Zip lng/lat together, and make a point out of each 
    points = gpd.GeoSeries([Point(lng, lat) for lng, lat in zip(lng_col, lat_col)] \
                           , name=name \
                           , index=index_col)
    return points



def hash_point(func):
    """Transform mutable shapely Point
    Into immutable
    Useful to be compatible with cache
    """
    class HPoint(Point):
        def __hash__(self):
            return hash(self.bounds)

    @wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([HPoint(arg) if isinstance(arg, Point) else arg for arg in args])
        kwargs = {k: HPoint(v) if isinstance(v, Point) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped


def in_polygon(point, polygon):
    """Simple wrapper on the within method of shapely points
    
    Params: point (POINT) a shapely point object
        polygon (POLYGON) a shapely polygon object (the target overlap area)
    
    Returns: (bool) whether or not the point is within polygon expressed as a boolean
    """
    return point.within(polygon)


def which_polygon(point, polygons):
    """Calls in_polygon and returns a pandas Series of boolean values for whether
    or not point is in each of a GeoSeries of polygons
    
    Params: point (POINT) a shapely point object
        polygons (GeoSeries) a GeoSeries of polygons to test
    
    Returns: (Series) a pandas Series of boolean values equivalent in length to [polygons]"""
    point_func = partial(in_polygon, point)
    return pd.Series(polygons.map(point_func))

@hash_point
@lru_cache()
def which_anc(point):
    """Calls which_polygon on gdf of DC ANCs, returns which ANC a point is in or 'Outside' if
    not in any ANC
    
    Params: point (POINT) a shapely point object
    
    Returns: ANC (str) string of the ANC point is within or 'Outside' if not in any ANC """
    

    # Build a series of boolean values corresponding to whether or not point is in each ANC geometry
    mask = which_polygon(point, gdf.geometry)
    
    result = None
    # If there is a true value return which ANC the point is in
    if any(mask):
        result = gdf.loc[mask, 'ANC_ID'].values[0]
    # If there are no true values return that the point is 'Outside' of DC
    else:
        result = 'Outside'
    
    return result

def station_to_anc(station):
    """DOCSTRING
    Accepts a string of station name, returns ANC station is in
    Make the unfound station a try except or assert or something"""
    # Find Station in stations_df
    row = stations_df.loc[stations_df.name == station]
    
    # If station not found
    if len(row) == 0:
        result = 'Unknown'
    
    # If Region ID is in outside regions, return outside
    # Do not check geometry
    elif row['region_id'].values[0] in (outside_regions):
        result = 'Outside'
        
    # If Region ID is not in outside regions
    # convert lat, lng to point obj. call which_anc
    # return result of which_anc
    else:
        point = Point(row.lon, row.lat)
        result = which_anc(point)
        
    return result
    

def station_anc_dict():
    """DOCSTRING"""
    
    station_anc_dict = {name: station_to_anc(name) for name in stations_df.name}
    return station_anc_dict

anc_dict = station_anc_dict()
station_keys = anc_dict.keys()


def anc_from_dict(station):
    """DOCSTRING"""
    # For each observation in a df, if there exists a station
    # pull the ANC from station_dict
    if station in station_keys:
        result = anc_dict[station]
    else:
        result = None
    
    return result    

def station_coords():
    """DOCSTRING
    Returns a Dataframe of Stations Currently on CABI API
    with lon/lat columns formatted into one coord_station column
    """
    curr_station_df = stations_df

    coords = point_series(
        curr_station_df['lon'],
        curr_station_df['lat'],
        name='coord_station',
        index_col=curr_station_df['name'])

    station_coords = curr_station_df.merge(
        coords,
        on='name'
    )

    station_coords = station_coords.drop(\
                                        ['region_id', 'lat', 'lon'],
                                         axis = 1)

    station_coords = gpd.GeoDataFrame(station_coords, geometry='coord_station')
    
    return station_coords

def in_dc(point):
    """Simple wrapper on the within method of shapely points
    
    Params: point (POINT) a shapely point object
    
    Returns: (bool) whether or not the point is within DC expressed as a boolean
    """
    
    return point.within(dc_boundary) 