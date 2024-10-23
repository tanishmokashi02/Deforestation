# -*- coding: utf-8 -*-
"""CNN_custom224.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/116_sachBMGk0rC8EXVYnQN8xNNWbtLyU
"""

# !pip install h5imagegenerator

import keras
import numpy as np
from keras.models import Sequential
from keras.utils import np_utils
from keras.layers import InputLayer, Conv2D, MaxPooling2D, GlobalAveragePooling2D, Flatten, Dense, Dropout
from keras.layers.experimental.preprocessing import RandomFlip, RandomRotation
from keras.preprocessing import image
import tensorflow as tf
from sklearn.model_selection import train_test_split
import PIL
import os
import cupy as cp
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import multilabel_confusion_matrix, classification_report, confusion_matrix
import h5py
from  h5imagegenerator import HDF5ImageGenerator

# files located in Google Drive
from google.colab import drive
drive.mount('/content/drive')

os.chdir('drive/My Drive/Metis/satellite_deforestation/')

import sys
sys.path.append('modules/')
import custom_metrics as cm

with open('data/tags.pickle','rb') as rf:
  tags = pickle.load(rf)

# data won't fit in memory so use a generator to feed it to the model in batches
train_generator = HDF5ImageGenerator(src='data/tensors_224.h5',
                                     X_key='X_train',
                                     y_key='y_train',
                                     labels_encoding=False,
                                     scaler=True,
                                     batch_size=128,
                                     mode='train')

test_generator = HDF5ImageGenerator(src='data/tensors_224.h5',
                                    X_key='X_test',
                                    y_key='y_test',
                                    labels_encoding=False,
                                    scaler=True,
                                    batch_size=128,
                                    mode='test')

# weight the weather classes less than others because they won't help identify deforestation
class_weights = {0: 0.75, 1: 1.0, 2: 0.75, 3: 0.5, 4: 0.5, 5: 0.5, 6: 0.5, 7: 1.0, 8: 1.0, 9: 1.0,
                 10: 0.5, 11: 0.5, 12: 0.75, 13: 1.0, 14: 1.0, 15: 1.0, 16: 0.75}

CNN = Sequential()

# series of 2D convolutional layers applied on 3x3 kernels followed by a 4:1 max pooling
# increase the number of filters in each subsequent layer so the model learns increasingly complex patterns
# add in dropout layers to help against overfitting

CNN.add(InputLayer(input_shape=(224,224,3)))
CNN.add(RandomRotation(0.25))  # randomly rotate images at 90 degree intervals (param is % of 2pi)
CNN.add(RandomFlip(mode='horizontal')) # randomly flip images horizontally (right hand becomes left hand)
CNN.add(Conv2D(filters=64,kernel_size=(3,3),activation='relu',padding='same'))
CNN.add(Conv2D(filters=64,kernel_size=(3,3),activation='relu',padding='same'))
CNN.add(MaxPooling2D(pool_size=(2,2)))
CNN.add(Dropout(0.25))
CNN.add(Conv2D(filters=128,kernel_size=(3,3),activation='relu',padding='same'))
CNN.add(Conv2D(filters=128,kernel_size=(3,3),activation='relu',padding='same'))
CNN.add(MaxPooling2D(pool_size=(2,2)))
CNN.add(Dropout(0.25))
CNN.add(Conv2D(filters=256,kernel_size=(3,3),activation='relu',padding='same'))
CNN.add(Conv2D(filters=256,kernel_size=(3,3),activation='relu',padding='same'))
CNN.add(MaxPooling2D(pool_size=(2,2)))
CNN.add(Dropout(0.25))
CNN.add(Conv2D(filters=512,kernel_size=(3,3),activation='relu',padding='same'))
CNN.add(Conv2D(filters=512,kernel_size=(3,3),activation='relu',padding='same'))
CNN.add(MaxPooling2D(pool_size=(2,2)))
CNN.add(Dropout(0.25))

# get everything in a single dimension before passing on to the fully connected layers
CNN.add(Flatten())

# CNN.add(Dense(64,activation='relu'))
CNN.add(Dense(17,activation='sigmoid')) # 17 output layers to match the 17 classes

CNN.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=[cm.challenge_score]  
)

CNN.summary()

# fit model and implement early stopping
CNN.fit(train_generator,
        epochs=30,
        class_weight=class_weights,
        workers=4,
        verbose=1,
        use_multiprocessing=True,
        callbacks=[
           keras.callbacks.ModelCheckpoint(
               'models/mnist.{epoch:02d}-{loss:.2f}.hdf5',
               save_best_only=True),
               keras.callbacks.EarlyStopping(patience=3,
                                             monitor='val_loss'),
               keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
               factor=0.5,
               patience=2,
               verbose=1,
               min_lr=0.0002)])

predictions = CNN.predict(test_generator,
        workers=2,
        verbose=1,
        use_multiprocessing=True)

f = h5py.File('data/tensors_224.h5','r') 
y_test = f['y_test'][:]

cm.item_accuracy(y_test,predictions)

cm.full_accuracy(y_test,predictions)

cm.challenge_score(y_test,predictions)

cm.multi_class_confusion(y_test,predictions,tags)

CNN.save('CNN_Custom')

