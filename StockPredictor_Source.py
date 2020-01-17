import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import tensorflow as tf
from yahoo_fin.stock_info import get_analysts_info, get_balance_sheet, get_live_price, get_data
import pandas_datareader as web
import requests_html
import csv
from google.colab import files

today = str(dt.date.today())
print(today)
start = "2018-01-01"
tickers = pd.read_csv('/content/complete.csv')
len(tickers)

#FIrst return vector
ret_cost = web.get_data_yahoo(tickers['Symbol'][0], start = start, end = today)
ret_cost = np.array(ret_cost['Adj Close'].ffill().pct_change())
ret_cost = ret_cost.reshape(ret_cost.shape[0],1)
#Second return vector
vec = web.get_data_yahoo(tickers['Symbol'][1], start = start, end = today) 
vec = np.array(vec['Adj Close'].ffill().pct_change())
vec = vec.reshape(vec.shape[0],1)
#Matrix building
ret_cost = np.hstack((ret_cost,vec))


ejected = 0
for var in range(1,len(tickers)) :
  try:
    vec = web.get_data_yahoo(tickers['Symbol'][var], start = start, end = today) 
    vec = np.array(vec['Adj Close'].ffill().pct_change())
    vec = vec.reshape(vec.shape[0],1)
    if vec.shape[0]==ret_cost.shape[0]:
      ret_cost = np.hstack((ret_cost,vec), )
      print(vec[1])
    else:
      print("padding avoided, SKIP at", var)
      ejected = ejected + 1
  except:
    print('EJECT at:', var)
    ejected = ejected + 1
  print(ret_cost.shape)
 
#Data Clearing
###Erasing FIRST ROW 
clean_ret = np.delete(ret_cost, 0, 0)
clean_ret = np.delete(clean_ret, obj=clean_ret.shape[0]-1, axis=0)

###LAST ROW TO FORECAST
to_forecast = ret_cost[477]

Y = web.get_data_yahoo('^GSPC', start = start, end = today)
Y = np.array(Y['Adj Close'].ffill().pct_change())
Y = Y.reshape(Y.shape[0],1)
Y = np.delete(Y, 0, 0)
Y = np.delete(Y, 0, 0)
print(clean_ret.shape, Y. shape)

#Saving Dataset
from google.colab import drive
drive.mount('/content/drive')
np.savetxt("DATA.csv", clean_ret, delimiter=",")
np.savetxt("S&P.csv", Y, delimiter=",")

clean_ret = pd.read_csv("/content/drive/My Drive/colab_notebooks/DATA.csv") 
Y = pd.read_csv("/content/drive/My Drive/colab_notebooks/S&P.csv")

#Classifying returns
rating = np.empty(len(Y), dtype=int)

for i in range(0,len(Y)):
  if Y[i] >= 0.02 :
    rating[i] = 4
  elif Y[i] < 0.02 and Y[i] >= 0 :
    rating[i] = 3
  elif Y[i] < 0 and Y[i] > -0.02 :
    rating[i] = 2
  elif Y[i]<-0.02 :
    rating[i] = 1
    
    
x_train, x_test, y_train, y_test, rating_train, rating_test = train_test_split(clean_ret, Y, rating, test_size=0.3, stratify=rating)
days = x_train.shape[0]
ones = np.ones((days, 1))

#Classification and Regression
from numpy.linalg import inv
import statistics
from keras import Sequential, optimizers
from keras.layers import Dense, Conv1D, Conv2D, MaxPooling2D, Flatten, Dropout
from sklearn.model_selection import train_test_split


# Now estimate the regression parameters from the data
returns = np.hstack((np.ones((x_train.shape[0], 1)), x_train))
S = np.dot(returns.T, returns)
S_inv = np.linalg.inv(S)
theta_hat = S_inv.dot(returns.T).dot(y_train)
print('Estimated theta: {}'.format(theta_hat))

reg_test = np.dot(np.hstack((np.ones((x_test.shape[0], 1)), x_test)),theta_hat)
regr_rati = np.empty(len(reg_test), dtype=int)
for i in range(0,len(reg_test)):
  if reg_test[i] >= 0.02 :
    regr_rati[i] = 4
  elif reg_test[i] < 0.02 and reg_test[i] >= 0 :
    regr_rati[i] = 3
  elif reg_test[i] < 0 and reg_test[i] > -0.02 :
    regr_rati[i] = 2
  elif reg_test[i]<-0.02 :
    regr_rati[i] = 1

np.mean(np.subtract(rating_test,regr_rati))
print(np.mean(np.subtract(x_test,reg_test)),np.max(reg_test))


# Basic Network

### Build model
model = Sequential()
model.add(Dense(300, activation='relu'))
model.add(Dense(150, activation='relu'))
model.add(Dense(1,activation='relu'))

### Compile model
model.compile(optimizer='sgd', loss='mean_squared_error', metrics=['accuracy'])
model.fit(x_train,y_train, epochs=30, validation_data=(x_test, y_test))


#Convolutional model
model = Sequential()
model.add(Conv2D(50, (3, 3), activation='tanh', input_shape= (,505) ) )
model.add(Conv2D(100, (3, 3), activation='tanh'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(300, activation='tanh'))
model.add(Dense(128, activation='tanh'))
model.add(Dense(50, activation='tanh'))
model.add(Dense(1, activation='tanh'))

model.compile(optimizer='sgd', loss='mean_squared_error', metrics=['accuracy'])
model.fit(x_train,y_train, epochs=30, validation_data=(x_test, y_test))


#Advanced Networks

### Standardize data
X = (clean_ret - clean_ret.mean(0)) / clean_ret.std(0)

legendary = np.empty(len(rating), dtype=int)
for i in range(0,len(rating)):
  if rating[i] >= 4 :
    legendary[i] = 1
  else :
    legendary[i] = 0

### Split train / test / validation data
X_train, X_test, y_train, y_test = train_test_split(X, legendary, test_size=0.1, stratify=legendary)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.1, stratify=y_train)

### Compute class weights
days = X_train.shape[0]
n_legendaries = legendary.sum()
n_classes = 2
class_weights = {0: days / (n_classes * (days - n_legendaries)), #common weight
                 1: days / (n_classes * n_legendaries)}          #legendary weight

print('Training data: {} legendaries out of {} days'.format(n_legendaries, days))
print('Training data: class weights {}'.format(class_weights))
print(X_train.shape)

network=Sequential()
network.add(Dense(32, activation='relu', input_shape=X.shape[1:]))
network.add(Dense(10, activation='relu'))
network.add(Dense(5, activation='relu'))
network.add(Dense(1, activation='softmax'))
network.compile(optimizer='sgd', loss='binary_crossentropy', metrics=['accuracy'], weighted_metrics=['accuracy'] )
network.fit(X_train, y_train, epochs=100,validation_data=[X_val,y_val] ,class_weight=class_weights)

train_scores = network.evaluate(X_train,y_train, verbose=0)
val_scores = network.evaluate(X_val,y_val, verbose=0)
print('Test loss: {} - Test acc: {}'.format(*train_scores))
print('Validation loss: {} - Validation Acc:{}'.format(*val_scores))
pd.DataFrame(network.history.history).plot()
plt.legend()
plt.grid(True)
plt.gca().set_ylim(0,1)
plt.show()


