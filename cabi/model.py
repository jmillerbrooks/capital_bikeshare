import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

def persistence_model(series):
    """DOCSTRING
    Wrapper for baseline persistence model"""
    return [x for x in series]





def test_stationarity(series, print_vals=True):
    """Simple wrapper around adfuller that prints in more readable format
    Adapted slightly from Jason Brownlee's machinelearningmastery.com
    
    Params:
        series (series) a timeseries
    Returns:
        adfuller test result"""
    
    result = adfuller(series)
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))
    return result

def RMSE(y_true, y_pred, last_only=True):
    """Simple wrapper function on mean_squared_error to return RMSE
    
    Params:
        predictions (series or array like object), the predicted values from model
        test_data (series or array like object), the true target values
        
    Returns:
        RMSE (list) list of accumulated RMSE values for each observation in consecutive time order
        i.e. the first return value will be just the error of first prediction, second the sqrt of mean squared error for first 2 predictions, etc."""

    rmse = None
    # Ensure predictions and test_data are same size
    if len(y_pred) != len(y_true):
        rmse = "Test data and predictions must have equal length"
    # If last_only is false, return the rmse for every point in the prediction set
    # (useful for tracking where model went wrong)
    elif last_only == False:
        rmse = [mean_squared_error(y_true[:i+1], y_pred[:i+1], squared=False) for i, _ in enumerate(y_pred)]
    # Normal case: return the rmse value for the full prediction set    
    else:
        rmse = mean_squared_error(y_true, y_pred, squared=False)
    
    return rmse

def fit_sarimax(series, cfg = [(0,1,1), (0,1,1,24), 'n'], test_start = '2020-07-01 00:00:00'):
    """DOCSTRING accepts a series and SARIMAX configuration, returns model object, train/test sets"""
    train = hourly[hourly.index < test_start]
    test = hourly[test_start:]
    
    model = SARIMAX(train, order=cfg[0], seasonal_order=cfg[1], trend=cfg[2])
    
    return train, test, model
    


def sarima_configs(seasonal=[1, 24, 168]):
    """build configuration list to do light gridsearch of SARIMAX models, function is from Jason Brownlee's website:
    machinelearningmastery.com """
    
    models = list()
    # define config lists
    p_params = [0, 1, 2]
    d_params = [0, 1]
    q_params = [0, 1, 2]
    t_params = ['n','c','t','ct']
    P_params = [0, 1, 2]
    D_params = [0, 1]
    Q_params = [0, 1, 2]
    m_params = seasonal
    # create config instances
    for p in p_params:
        for d in d_params:
            for q in q_params:
                for t in t_params:
                    for P in P_params:
                        for D in D_params:
                            for Q in Q_params:
                                for m in m_params:
                                    cfg = [(p,d,q), (P,D,Q,m), t]
                                    models.append(cfg)
    return models





def SARIMAX_error(series, p=10, d=2, q=2):
    """Simple wrapper that fits SARIMAX model and returns RMSE (raw and pct) for the predictions, confidence interval, start of forecast and end of actual 
    values"""
    
    
    X = series
    
    # set trainset to include all but last 48 months (4 years) only training on data between 9-4 years ago
    train_size = int(len(X) - 48)
    train, test = X[-108:train_size], X[train_size:]

    model = SARIMAX(train, order=(p,d,q), freq='MS',  initialization='approximate_diffuse')

    results = model.fit()

    # Predict 48 months from end of train set
    forecast = results.get_forecast(steps=48)
    pred_ci = forecast.conf_int(alpha=.05)

    predictions = forecast.predicted_mean

    rmse = RMSE(test, predictions)
    pct = error_as_pct(rmse, train[-1], test[-1])
    
    return pred_ci, rmse, pct, (train[-1], test[-1])



def SARIMAX_forecast(series, cfg, pred_len):
    """DOCSTRING"""
    
    
    X = series
    
    # set trainset to include all but last 48 months (4 years) only training on data between 9-4 years ago
    train_size = int(len(X) - pred_len)
    train, test = X[0:train_size], X[train_size:]

    model = SARIMAX(train, order=cfg[0], seasonal_order=cfg[1], trend=cfg[2], initialization='approximate_diffuse')

    results = model.fit()

    # Predict 48 months from end of train set
    forecast = results.predict(start=test.index[0], end=test.index[-1])
    
    return forecast

    
    
    
#     pred_ci = forecast.conf_int(alpha=.05)

#     predictions = forecast.predicted_mean

#     rmse = RMSE(test, predictions)
#     pct = error_as_pct(rmse, train[-1], test[-1])
    
#     ROI = (predictions[-1] - train[-1]) / train[-1]
    
#     #return {'pred_ci': pred_ci, 'rmse': rmse, 'pct_error': pct, 'test': test, 'predictions': predictions, 'series': X}
#     return ROI