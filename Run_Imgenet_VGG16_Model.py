import os
import glob
import re
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from keras.models import Sequential
from keras.models import Model
from keras.layers import Dense
from keras.layers import Conv2D
from keras.layers import MaxPool2D
from keras.layers import Flatten
from keras import optimizers
from keras.layers import Dropout
from keras.applications.vgg16 import VGG16
from keras.utils.vis_utils import plot_model
from keras.applications.vgg16 import decode_predictions
from tensorflow.keras.layers import LeakyReLU

from CQ500DataGenerator import DataGenerator

import pickle

# define our variables
data_dir = '/Users/zhengma/Documents/ConvOuch/Data/'
num_slices_original = 28
num_slices_per_subject = 24       # always using 16 slices per subject
start_slice = (num_slices_original - num_slices_per_subject)/2
end_slice = start_slice + num_slices_per_subject

start_slice = int(start_slice)
end_slice = int(end_slice)

# create list of IDs from all slices
all_IDs = set()
all_Slices = glob.glob(data_dir + "Slices/CQ500-CT-*")
for item in all_Slices:
    subj_match = re.match(data_dir + "Slices/(CQ500-CT-[0-9]+)_Slice[0-9]+.npy", item)
    subj_id = subj_match.group(1)
    all_IDs = all_IDs.union([subj_id])

# use half of the IDs for testing
all_IDs = list(all_IDs)
half = int(np.floor(len(all_IDs)/10*9))
all_IDs = all_IDs[0:half]

all_IDs_slices = list()
for subj_id in all_IDs:
    for slice_num in range(start_slice, end_slice):
        all_IDs_slices.append(subj_id + "_Slice" + str(slice_num))


# # create a dict of labels for all slices
# all_labels = dict()
# label_files = glob.glob(data_dir + "Labels/CQ500-CT-*")
# for item in label_files:
#     slice_match = re.match(data_dir + "Labels/(CQ500-CT-[0-9]+)_Slice([0-9]+).npy", item)
#     subj_id = slice_match.group(1)
#     slice_num = slice_match.group(2)
#     # data_obj = np.load(item)
#     data_dict = data_obj.item()
#     all_labels[subj_id + "_Slice" + slice_num] = int(data_dict["label"])    # store labes as 1 or 0 for True or False


# divide list into train and validation
percentage_to_train = 0.8
cutoff_index = int(np.floor(len(all_IDs) * percentage_to_train)) * num_slices_per_subject
training_IDs = all_IDs_slices[0:cutoff_index]
validation_IDs  = all_IDs_slices[cutoff_index:]

training_generator = DataGenerator(training_IDs)
validation_generator = DataGenerator(validation_IDs)

# num_train_set = 40


#add our own fully connected layers for the final classification

# create the base pre-trained model
base_model = VGG16(include_top=False, weights='imagenet', 
                    input_tensor=None, input_shape=(224, 224, 3), pooling=None)

#now we can start to fine-tune the model
# first: train only the top layers (which were randomly initialized)
# i.e. freeze all convolutional InceptionV3 layers
for layer in base_model.layers:
    layer.trainable = False

x = base_model.output
#flatten it
x = Flatten()(x)
x = Dropout(0.2)(x)
# let's add a fully-connected layer
x = Dense(100, activation='relu')(x)
x = Dropout(0.2)(x)
#x = LeakyReLU(alpha=.01)(x)
x = Dense(100, activation='relu')(x)
x = Dropout(0.2)(x)

#another fully-connected layer
#x = Dense(200, activation='relu')(x)
# and a logistic layer -- let's say we have 200 classes
predictions = Dense(2, activation='softmax')(x)

# this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)

print(model.summary())

my_optimizer=optimizers.Adam(lr=0.00001)

# compile the model (should be done *after* setting layers to non-trainable)
model.compile(loss='categorical_crossentropy', optimizer=my_optimizer, metrics=['accuracy'])
history = model.fit_generator(generator=training_generator, validation_data=validation_generator, epochs=5, use_multiprocessing=False)
    
model.save('FifthModel.h5')

with open('FifthModel_trainHistoryDict', 'wb') as file_pi:
        pickle.dump(history.history, file_pi)

