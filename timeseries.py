# -*- coding: utf-8 -*-
"""TimeSeries.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1g5NLKpKVjeST-OSBkqvjdCfHCo9PLAHk

Nama  : Muhammad Zhafran Ghaly

ID    : m183x0348


Kelas : M02


Divisi: Machine Learning and Front-End
"""

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv('BTC-USD.csv')
df.head(10)

df.isnull().sum()

df.shape

date = df['Date'].values
open = df['Open'].values
plt.figure(figsize = (10,10))
plt.plot(date, open)
plt.title('Open price of BTC',
          fontsize = 20);

cols = [0,1]
df = df[df.columns[cols]]
df

open = open.reshape(-1, 1)
scaler = MinMaxScaler()
scaled_open = scaler.fit_transform(open)
scaled_open = scaled_open.reshape(1, -1)
scaled_open = np.hstack(scaled_open)
scaled_open

X_train, X_test, y_train, y_test = train_test_split(
                                    date,
                                    scaled_open, 
                                    test_size=0.2, 
                                    random_state=1, 
                                    shuffle=False)

print(len(X_train), len(X_test))

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis = -1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift = 1, drop_remainder = True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

def model_forecast(model, series, window_size):
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size, shift = 1, drop_remainder = True)
    ds = ds.flat_map(lambda w: w.batch(window_size))
    ds = ds.batch(32).prefetch(1)
    forecast = model.predict(ds)
    return forecast

training_set = windowed_dataset(y_train, window_size = 64, 
                             batch_size = 200, 
                             shuffle_buffer = 1000)
validation_set = windowed_dataset(y_test, window_size=64,
                           batch_size=200,
                           shuffle_buffer=1000)

model = tf.keras.Sequential([
   
    tf.keras.layers.LSTM(60, return_sequences=True),
    tf.keras.layers.LSTM(60),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(10, activation="relu"),
    tf.keras.layers.Dense(1)
])

model.compile(loss="mean_squared_error",
              optimizer="adam",
              metrics=['accuracy'])

gauge = (max(scaled_open) - min(scaled_open)) * 0.1
print(gauge)

class Callbackhx(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae') < gauge) and (logs.get('val_mae') < gauge):
      self.model.stop_training = True
      print('\nFor Epoch', epoch, ' training has been stopped.''\n Because MAE of the model has reach < 10% of data scale')
callbacks = Callbackhx()

optimizer = tf.keras.optimizers.SGD(learning_rate = 1.0000e-04, momentum = 0.9)
model.compile(loss = tf.keras.losses.Huber(),
              optimizer = optimizer,
              metrics = ["mae"])

history = model.fit(
    training_set,
    epochs = 100, 
    validation_data = validation_set,
    callbacks = [callbacks]
)

plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('Model Accuracy')
plt.ylabel('Mae')
plt.xlabel('epochs')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epochs')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()