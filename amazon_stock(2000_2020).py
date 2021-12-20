# -*- coding: utf-8 -*-
"""Amazon_Stock(2000-2020).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nbnq97fJsRY1VKutWlecYJdRPzze0gTU
"""

import numpy as np
import pandas as pd
from google.colab import files
uploaded = files.upload()

# Commented out IPython magic to ensure Python compatibility.
from pandas import read_csv
from pandas import datetime
from matplotlib import pyplot as plt
# %matplotlib inline
import warnings
warnings.filterwarnings("ignore")
plt.rcParams["figure.figsize"] = (20,10) #Make the plots bigger by default
plt.rcParams["lines.linewidth"] = 2 #Setting the default line width
plt.style.use("Solarize_Light2") #Define the style of the plot
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.seasonal import seasonal_decompose #Describes the time data
from statsmodels.tsa.stattools import adfuller #Check if data is stationary
from statsmodels.graphics.tsaplots import plot_acf #Compute lag for ARIMA
from statsmodels.graphics.tsaplots import plot_pacf #Compute partial lag for ARIMA
from statsmodels.tsa.arima_model import ARIMA #Predictions and Forecasting
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS

print(plt.style.available)

Amazon=pd.read_csv("Amazon.csv")
print(Amazon)

Amazon.head(10)

print(Amazon.isnull().any())

amazonOpen = Amazon[["Date", "Open"]].copy() #Get the date and open columns
amazonOpen["Date"] = pd.to_datetime(amazonOpen["Date"]) #Ensure the date data is in datetime format
amazonOpen.set_index("Date", inplace = True) #Set the date to the index
amazonOpen = amazonOpen.asfreq("b") #Set the frequency
amazonOpen = amazonOpen.fillna(method  = "ffill") #Fill null values with future values
amazonOpen.head(15)

y = amazonOpen.plot(title = "Amazon Stocks (Open)") #Get an idea of the data
y.set(ylabel = "Price at Open") #Set the y label to open
plt.show() #Show the plot



plot_acf(amazonOpen['Open'], alpha =0.05)
plt.show()

plot_pacf(amazonOpen['Open'], alpha =0.05, lags=50)
plt.show()

df = pd.DataFrame(amazonOpen,columns=['Date','Open'])
X =np.arange(len(df[['Open']]))
Y = np.asarray(df[['Open']])
X = sm.add_constant(X)
ols_res = OLS(Y,X).fit()
durbin_watson(ols_res.resid)

"""Stationarity Test """

decomp = seasonal_decompose(amazonOpen, model = "multiplicative") #Decompose the data
x = decomp.plot() #Plot the decomposed data

print("ADFuller Test; Significance: 0.05") #Print the significance level
adf = adfuller(amazonOpen["Open"]) #Call adfuller to test
print("ADF test static is {}".format(adf[1])) #Print the adfuller results

openLog = np.log(amazonOpen) #Take the log of the set for normalization
openStationary = openLog - openLog.shift() #Get a stationary set by subtracting the shifted set
openStationary = openStationary.dropna() #Drop generated null values from the set
openStationary.plot(title = "Stationary Amazon Stocks") #Plot the stationary set

print("ADFuller Test; Significance: 0.05") #Print the significance level
adf = adfuller(openStationary["Open"]) #Call adfuller to test
print("ADF test static is {}".format(adf[1])) #Print the adfuller results

decomp = seasonal_decompose(openStationary) #Decompose the stationary data
x = decomp.plot() #Plot the decomposition

fig,axes = plt.subplots(2,2) #Set a subset for the data visualizations
a = axes[0,0].plot(amazonOpen["Open"]) #Plot the original data
a = axes[0,0].set_title("Original Data") #Give the original data a name
b = plot_acf(amazonOpen["Open"],ax=axes[0,1]) #Plot the ACF of the original data
x = axes[1,0].plot(openStationary["Open"]) #Plot the stationary data
x = axes[1,0].set_title("Stationary Data") #Give the stationary data a name
y = plot_acf(openStationary["Open"],ax=axes[1,1]) #Plot the ACF of the stationary data

fig,axes = plt.subplots(1,2) #Create a subplot for the Partial ACF
a = axes[0].plot(openStationary["Open"]) #Plot the stationary data
a = axes[0].set_title("Stationary") #Ensure the stationary data is named
b = plot_pacf(openStationary["Open"], ax = axes[1], method = "ols") #Plot the partial ACF

fig,axes = plt.subplots(1,2) #Create a subplot for the ACF
a = axes[0].plot(openStationary["Open"])#Plot the stationary data
a = axes[0].set_title("Stationary") #Ensure the stationary data is named
b = plot_acf(openStationary["Open"], ax = axes[1]) #Plot the ACF

model = ARIMA(openStationary, order = (5, 1, 5)) #Build the ARIMA model
fitModel = model.fit(disp = 1) #Fit the ARIMA model

plt.rcParams.update({"figure.figsize" : (12,6), "lines.linewidth" : 0.05, "figure.dpi" : 100}) #Fix the look of the graph, dimming it to show the red
x = fitModel.plot_predict(dynamic = False) #Fit the ARIMA model
x = plt.title("Forecast Fitting") #Add a stock title
plt.show() #Show the ARIMA plot

plt.rcParams.update({"figure.figsize" : (12,5), "lines.linewidth": 2}) #Fix the line width
length = int((len(amazonOpen)*9)/10) #Get 9/10 of the length of the data
print(length) #Print the length to make sure it actually is an int

train = amazonOpen[:length] #Use 9/10 of the data for the train set
test = amazonOpen[length:] #Use the rest for testing
modelValid = ARIMA(train,order=(5,1,5)) #Create a model for the train set
fitModelValid = modelValid.fit(disp= -1) #Fit the model

fc,se,conf = fitModelValid.forecast(len(amazonOpen) - length) #Forcast over the test area
forecast = pd.Series(fc, index = test.index) #Get the forecast for the area

#Add labels for the train, test, and forecast
plt.plot(train,label = "Training Data") 
plt.plot(test,label = "Actual Continuation")
plt.plot(forecast,label = "Forecasted Continuation", color = "g")
plt.title("ARIMA Forecast") #Add the Forecast title
plt.legend(loc = "upper left") #Put the legend in the top left
plt.xlabel("Year") #Add the year label to the bottom
plt.ylabel("Open Price") #Add the open price to the y axis

modelPred = ARIMA(amazonOpen,order=(5,1,5)) #Create a model for the whole data
fitModelPred = modelPred.fit(disp= -1) #Fit the model

fitModelPred.plot_predict(1,len(amazonOpen) + 1000) #Plot predictions for the next thousand days
x = fitModelPred.forecast(1000) #Forecast the prediction for the next thousand days.
x = plt.title("Amazon Stock Forecast") #Add a stock title
x = plt.xlabel("Year") #Add the year label to the bottom
x = plt.ylabel("Open Price") #Add the open price to the y axis