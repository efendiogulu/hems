from sklearn.base import TransformerMixin, BaseEstimator
import pandas as pd
import numpy as np

class HourOfDay(BaseEstimator, TransformerMixin):
    ''' Transformer that extracts the hour of day from the datetime index. '''
    def transform(self, X):
        return X.index.hour.values.reshape(-1, 1)

    def fit(self, X, y=None, **fit_params):
        return self

class DayOfWeek(BaseEstimator, TransformerMixin):
    ''' Transformer that extracts the day of the week from the datetime index. '''
    def transform(self, X):
        return X.index.dayofweek.values.reshape(-1, 1)
        
    def fit(self, X, y=None, **fit_params):
        return self
    
class MonthOfYear(BaseEstimator, TransformerMixin):
    ''' Transformer that extracts the month of the year from the datetime index. '''
    def transform(self, X):
        return (X.index.month - 1).values.reshape(-1, 1)
       
    def fit(self, X, y=None, **fit_params):
        return self
    
class Lags(BaseEstimator, TransformerMixin):
    ''' Transformer that creates lags as configured by the list. '''
    def __init__(self, lags=[1]):
        self.lags = lags

    def transform(self, X):
        X_prime = pd.DataFrame(index=X.index)

        for c in X:
            for l in self.lags:
                X_prime.loc[:,str(c) + "_" + str(l)] = X.loc[:, c].shift(l).copy()
        return X_prime.fillna(0.0)
    
    def fit(self, X, y=None, **fit_params):
        return self
    
    def get_feature_names():
        names =  []
        for c in self.columns:
            for l in self.lags:
                names.append(str(c) + "_" + str(l))
        return names
    
class Forecast(BaseEstimator, TransformerMixin):
    ''' Transformer that transposes the weather forecsat to be useful in forecasting. '''
    def __init__(self, H=1):
        self.H = H

    def transform(self, X):
        F = pd.DataFrame(index=X.index)
        for h in np.arange(0, self.H):
            for c in X:
                F[c + "_" + str(h)] = X.loc[:, c].shift(periods=-h)
        return F.fillna(0.0)
            
    def fit(self, X, y=None, **fit_params):
        return self
    
    def get_feature_names():
        names =  []
        for h in np.arange(0, self.H):
            names.append(self.columns + "_" + str(h))
            

class LabelToHorizon(BaseEstimator, TransformerMixin):
    ''' Transformer that creates a multi dimensional vector of the signal for time serie forecsating. '''
    def __init__(self, H):
        self.H = H

    def transform(self, y):
        F = pd.DataFrame(index=y.index)
        for h in np.arange(0, self.H):
            F[str(h)] = y.shift(periods=-h)
        return F.fillna(0.0)

    def fit(self, y):
        return self