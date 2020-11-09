import pandas as pd
import numpy as np
from scipy.stats import mode
from functools import partial
import pmdarima.preprocessing as ppc
from statsmodels.tsa.deterministic import CalendarSeasonality


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

# Figure out how computationally expensive it would be to store all results including the exogenous columns


def to_plus_minus(df, col='ANC'):
    """DOCSTRING, accepts a location column, returns a df where the columns correspond to
    the values of the col passed in params, values of each column are a timeseries of gain/loss
    values one of (-1,0,1) yielded from net_gain_loss_location"""

    # Build iterable of locations from unique values of a column, ignoring entries that are not in an ANC
    # This is an area for future improvement, see for example map of rides that did not end in ANC but started
    # Outside of DC, there is a clear edge effect, indicating that a better approach here would be to cluster
    # locations throught the entire region rather than using the rather arbitrary ANC tiling
    # used here for expediency to limit scope of the project
    locations = locations = [
        location for location in df[col].unique() if location != 'Outside']

    # Create dictionary of locations (keys) and series of plus minus values returned
    # from net_gain_loss(location, df, col=col) for each unique location in locations
    plus_minus_dict = {location: net_gain_loss(location, df, col)
                       for location in
                       locations}
    # Convert dict to dataframe, index by the (time) index of long_anc_df passed
    plus_minus_df = pd.DataFrame(plus_minus_dict, index=df.index)

    return plus_minus_df


def cumulative_change(df, window_size):
    """DOCSTRING window_size must be an int or offset passable to pandas.DataFrame.rolling(window)
    intended for use as an offset"""
    rolling_df = df.rolling(window_size).sum()
    return rolling_df


def series_to_interval(series, interval):
    """DOCSTRING take mode accross each one hour period if there are values, if no values, i.e. mode returns na like, presumed change is zero"""
    regular = series.resample(
        interval
    ).apply(
        lambda x:
        mode(x)[0] if mode(x)[0].size > 0
        else np.nan
    ).interpolate('time')

    return regular


def snap_to_interval(df, interval):
    change_func = partial(series_to_interval, interval=interval)
    return df.apply(change_func)


def get_seasonal_dummies(df):
    """Accepts a time-indexed df of hourly data, returns hourly and weekday dummies as a df
    to passed as exogenous variables in a SARIMAX model"""
    columns = df.columns
    new_df = df.copy()
    new_df['time'] = new_df.index

    # create weekday dummy generator
    wday_dumgen = ppc.DateFeaturizer(
        column_name='time', with_day_of_month=False)

    # since all have the same index, we can use any column in the df to generate the day_dums
    _, wday_dums = wday_dumgen.fit_transform(new_df[columns[0]], new_df)

    # drop the columns that aren't dummies
    wday_dums = wday_dums[wday_dums.columns[-7:]]

    # set the index for easy merging
    wday_dums.set_index(new_df.index, inplace=True)

    # create hourly dummy generator
    hourly_dumgen = CalendarSeasonality('H', 'D')

    # generate dummies
    hourly_dums = hourly_dumgen.in_sample(new_df.index)

    # merge results
    full_dums = wday_dums.merge(hourly_dums, on='time')

    return full_dums
