#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 18:36:34 2019

@author: mert
"""

import pandas as pd # work with data
from pandas import ExcelWriter
import numpy as np # work with matrices and vectors
from sqlalchemy import create_engine # database
import requests # rest web services
import pytz # timezones

# machine learning
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline, make_union
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler
from sklearn.compose import make_column_transformer
from sklearn.model_selection import train_test_split, TimeSeriesSplit, KFold, GridSearchCV
from sklearn.multioutput import MultiOutputRegressor, RegressorChain

from quantile import QuantileRegressor
from features import *

import datetime 

from scipy.stats import multivariate_normal, norm, uniform
import scipy.interpolate as interpolate

# plotting libraries
#from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#import plotly.graph_objs as go
import matplotlib.pyplot as plt
import seaborn as sns




energy = pd.read_csv('energy.csv')
holidays = pd.read_csv('holidays.csv') #holidays in Germany
weather = pd.read_csv('temperature.csv') #Temperature in Fahrenheit

energy['time_stamp'] = pd.Series(pd.date_range(start='1/1/2018', end='1/1/2019', freq='15min'))
energy['day_time'] = energy['time_stamp'].dt.date
energy['day_time'] = pd.to_datetime(energy['day_time'])
energy['hour'] =  energy['time_stamp'].dt.hour 

energy['lag_1'] = energy['ph'].shift(1)

holidays = holidays[(holidays['holiday_date'] >= '2018-01-01') & (holidays['holiday_date'] < '2019-01-01')]
holidays['holidays_date'] = pd.to_datetime(holidays['holiday_date'])
holidays = holidays[holidays['holiday_type'].str.contains("national")]
holidays['is_holiday'] = 1 
holidays = holidays[['holiday_date', 'is_holiday']]
holidays = holidays.rename(index=str, columns={"holiday_date": "day_time"})
holidays['day_time'] = pd.to_datetime(holidays['day_time'])

df = pd.merge(energy, holidays, how='outer', on='day_time')
df = df.fillna(value=0)

weather = weather.rename(index=str, columns={"Date": "day_time", "Temperature.Fahrenheit": "fahrenheit" })
weather = weather[(weather['day_time'] >= '2018-01-01') & (weather['day_time'] < '2019-01-01')]
weather['day_time'] = pd.to_datetime(weather['day_time'])
weather = weather[['day_time', 'fahrenheit']]

df = pd.merge(df, weather, how='outer', on='day_time')
df['day_of_week'] = df['day_time'].dt.dayofweek
df['day_name'] = df['day_time'].apply(lambda x: datetime.datetime.strftime(x, '%A'))
df['month_name'] = df['day_time'].apply(lambda x: datetime.datetime.strftime(x, "%B"))

one_hot_day = pd.get_dummies(df['day_name'])
df = df.drop('day_name',axis = 1)
df = df.join(one_hot_day)

one_hot_month = pd.get_dummies(df['month_name'])
df = df.drop('month_name',axis = 1)
df = df.join(one_hot_month)
df = df.drop(['day_time','day_of_week', 'Friday', 'December'],axis = 1)

y = pd.DataFrame(df['ph'])
X = df.drop(['ph','time_stamp'],axis = 1)


scenario_X_train, scenario_X_test, scenario_y_train, scenario_y_test = train_test_split(X, y, test_size=0.25, shuffle=False)

scenario_y_hat =  []
for quantile in [0.01, 0.05,0.1, 0.2 , 0.25, 0.5, 0.75, 0.9, 0.95, .99]:
    qr = MultiOutputRegressor(QuantileRegressor(quantile=quantile))
    qr.fit(scenario_X_train, scenario_y_train)
    scenario_y_hat.append(qr.predict(scenario_X_test))


scenario_y_hat = np.array(scenario_y_hat).transpose(1, 2, 0)
scenario_y_hat = np.squeeze(scenario_y_hat)

scenario_y_hat_data_frame = pd.DataFrame(scenario_y_hat)

scenario_y_test_data_frame = pd.DataFrame(scenario_y_test)
asil = scenario_y_test_data_frame.reset_index(drop=True)
all_data = pd.concat([scenario_y_hat_data_frame, asil], axis=1)


#
#This part is just to present a small portion of results
#
all_data[:24]
plt.rcParams["figure.figsize"] = [16,9]

plt.plot(all_data[0][:100], color = 'black')
plt.plot(all_data['ph'][:100], color = 'blue')
plt.plot(all_data[1][:100], color = 'red')
plt.plot(all_data[2][:100], color = 'brown')
plt.plot(all_data[3][:100], color = 'green')
plt.plot(all_data[5][:100], color = 'yellow')
plt.plot(all_data[4][:100], color = 'gray')
plt.plot(all_data[6][:100], color = 'm')
plt.plot(all_data[7][:100], color = '0.75')


writer = ExcelWriter('scenarios.xlsx')
all_data.to_excel(writer)
writer.save()
