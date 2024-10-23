# -*- coding: utf-8 -*-
"""new_imagery.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1F2P6tuMahKX6UOENCq1d_GGysBLRieHm
"""

import keras
import os
import numpy as np

from google.colab import drive
drive.mount('/content/drive')

os.chdir('drive/My Drive/Metis/satellite_deforestation')

import sys
sys.path.append('modules/')
import custom_metrics as cm
from image_to_tensor import image_to_tensor

cnn = keras.models.load_model('CNN_Custom',custom_objects={'cm.full_accuracy': cm.full_accuracy})

test_images = []
for img in os.listdir('images/new/'):
  arr = image_to_tensor(img)
  test_images.append(arr)

new_img_array = np.stack([arr for arr in test_images])

cnn.predict(new_img_array)