import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_pacf, plot_acf

def plot_trips(df):
    ax = gdf.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')
    sns.scatterplot(x='start_lng', y='start_lat', data=df, ax=ax)
    pass

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


        