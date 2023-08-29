# Make tf.data.Datasets from ERA5 monthly precip

import os
import sys
import random
import tensorflow as tf
import numpy as np

from localise import ModelName


# Load a pre-standardised tensor from a file
def load_tensor(file_name):
    sict = tf.io.read_file(file_name)
    imt = tf.io.parse_tensor(sict, np.float32)
    imt = tf.reshape(imt, [721, 1440, 1])
    return imt


# Get a list of filenames containing tensors
def getFileNames(purpose, nMonths=None, startyear=None, endyear=None):
    inFiles = sorted(
        os.listdir("%s/MLP/%s/datasets/%s" % (os.getenv("SCRATCH"), ModelName, purpose))
    )
    if startyear is not None:
        inFiles = [fn for fn in inFiles if int(fn[:4]) >= startyear]
    if endyear is not None:
        inFiles = [fn for fn in inFiles if int(fn[:4]) <= endyear]
    if nMonths is not None:
        if len(inFiles) >= nMonths:
            inFiles = inFiles[0:nMonths]
        else:
            raise ValueError(
                "Only %d months available, can't provide %d" % (len(inFiles), nMonths)
            )
    return inFiles


# Get a dataset
def getDataset(
    purpose, nMonths=None, startyear=None, endyear=None, shuffle=True, cache=False
):
    # Get a list of filenames containing tensors
    inFiles = getFileNames(
        purpose, nMonths=nMonths, startyear=startyear, endyear=endyear
    )
    if shuffle:
        random.shuffle(inFiles)

    # Create TensorFlow Dataset object from the source file names
    tn_data = tf.data.Dataset.from_tensor_slices(tf.constant(inFiles))

    # Convert from list of file names to Dataset of source file contents
    fnFiles = [
        "%s/MLP/%s/datasets/%s/%s" % (os.getenv("SCRATCH"), ModelName, purpose, x)
        for x in inFiles
    ]
    ts_data = tf.data.Dataset.from_tensor_slices(tf.constant(fnFiles))
    ts_data = ts_data.map(load_tensor, num_parallel_calls=tf.data.experimental.AUTOTUNE)

    # Zip the data together with the filenames (so we can find the date and source of each
    #   data tensor if we need it).
    tz_data = tf.data.Dataset.zip((ts_data, tn_data))

    # Optimisation
    if cache:
        tz_data = tz_data.cache()  # Great, iff you have enough RAM for it

    tz_data = tz_data.prefetch(tf.data.experimental.AUTOTUNE)

    return tz_data
