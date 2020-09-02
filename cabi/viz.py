import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_pacf, plot_acf
from cabi.etl.get_data import anc_gdf

gdf = anc_gdf()

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




        