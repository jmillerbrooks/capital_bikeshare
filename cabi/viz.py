import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_pacf, plot_acf
from cabi.etl.extract import anc_gdf
import datetime as dt

gdf = anc_gdf()

def plot_trips(df):
    ax = gdf.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')
    sns.scatterplot(x='start_lng', y='start_lat', data=df, ax=ax)
    pass

def plot_daily_counts(daily_counts):
    """Helper function for streamlining technical notebook"""
    fig, (axe, axe1, axe2) = plt.subplots(3, 1, sharey=True, figsize=(24, 9))

    plt.style.use('seaborn-deep')


    daily_counts = daily_counts.rideable_type

    nineteen = daily_counts[(daily_counts.index < '2020-01-01') & (daily_counts.index > '2019-01-01')]
    eighteen = daily_counts[daily_counts.index < '2019-01-01']
    twenty = daily_counts[daily_counts.index >= '2020-01-01']

    # Moving averages
    rolling_eighteen = eighteen.rolling(window=15).mean()
    rolling_nineteen = nineteen.rolling(window=15).mean()
    rolling_twenty = twenty.rolling(window=15).mean()


    axe.plot(eighteen)
    axe.plot(rolling_eighteen, color = 'green')
    axe.axhline(y=12500, ls = '--', color='navy')
    axe.axhline(y=2500, ls = '--', color='orangered')
    axe.set_xlim([dt.date(2018, 1, 1), dt.date(2018, 12, 31)])

    axe1.plot(nineteen)
    axe1.plot(rolling_nineteen, color = 'green')
    axe1.axhline(y=12500, ls = '--', color='navy')
    axe1.axhline(y=2500, ls = '--', color='orangered')
    axe1.set_xlim([dt.date(2019, 1, 1), dt.date(2019, 12, 31)])


    axe2.plot(twenty)
    axe2.plot(rolling_twenty, color = 'red')
    axe2.axhline(y=12500, ls = '--', color='navy')
    axe2.axhline(y=2500, ls = '--', color='orangered')
    axe2.set_xlim([dt.date(2020, 1, 1), dt.date(2020, 12, 31)])

    
    fig.suptitle('Daily Capital Bikeshare Ride Counts, 2018-2020', y=1.06, fontsize=28)
    fig.text(s='Green and Red Lines are 15 Day Moving Averages', x=0.5, horizontalalignment='center', y=.99, fontsize=20)
    fig.tight_layout()
    # fig.savefig('../figures/dailyridecounts.png', bbox_inches='tight')

    return fig, (axe, axe1, axe2)




def plot_acf_pacf(series, nlags):
    plt.figure(figsize=(15,10))
    plt.subplot(211)
    plot_acf(series, lags=nlags, ax=plt.gca())
    plt.subplot(212)
    plot_pacf(series, lags=nlags, ax=plt.gca())
    plt.show()


def plot_series(series, train_end=None, preds=[], fig_size=(10,10)):
    """Wrapper to quickly produce a plot of a time series, with
    optional params train_end (datetime appearing in index of series/ preds)
    and preds to visualize forecasting as well.
    If preds is passed train_end must also be specified."""
    if any(preds):
        fig, ax = plt.subplots(figsize=fig_size)
        series[:train_end].plot(label='Train', ax=ax)
        series[train_end:].plot(label='Test', ax=ax)
        preds[train_end:].plot(label='Out of Sample Forecast', ax=ax)
        preds[:train_end].plot(label='In Sample Predictions', ax=ax)
        ax.set_title(f'Model Predictions for {series.name}')
        plt.legend(loc='upper left')
        fig.tight_layout()
        plt.show();
    # For plotting train/test data without predictions
    elif train_end:
        fig, ax = plt.subplots(figsize=fig_size)
        series[:train_end].plot(label='Train', ax=ax)
        series[train_end:].plot(label='Test', ax=ax)
        ax.set_title(f'Train and Test sets for {series.name}')
        plt.legend(loc='upper left')
        fig.tight_layout()
        plt.show();
    else:
        fig, ax = plt.subplots(figsize=fig_size)
        series.plot(label=f'{series.name}', ax=ax)
        ax.set_title(f'{series.name}')
        plt.legend(loc='upper left')
        fig.tight_layout()
        plt.show();
    
    return fig, ax

def residual_plot(model):
    """DOCSTRING, wrapper to quickly plot residuals for a model object
    Accepts fitted model object
    Returns fig, ax with the residual plot
    """
    
    residuals = model.resid.values
    pred_vals = model.predict().values

    fig, ax = plt.subplots(figsize=(10,10))

    plt.scatter(x=pred_vals, y=residuals, ax=ax)
    
    # Use get params or something to label this
    ax.set_title('Residual Plot of Model Predictions')
    ax.set_xlabel('Prediction (change in number of bikes)')
    ax.set_ylabel('Residual (Error) - difference from actual change in number of bikes')
    
    plt.show();
    
    return fig, ax




        