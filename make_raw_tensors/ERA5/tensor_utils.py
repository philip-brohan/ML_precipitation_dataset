# Utility functions for creating and manipulating raw tensors

import tensorflow as tf

from get_data.ERA5 import ERA5_monthly
from utilities import grids

# Load the data for 1 month (on the standard cube).
def load_raw(year, month, member=None, variable="total_precipitation"):
    raw = ERA5_monthly.load(
        variable=variable,
        year=year,
        month=month,
        grid=grids.E5sCube,
    )
    return raw


# Convert raw cube to tensor
def raw_to_tensor(raw):
    ict = tf.convert_to_tensor(raw.data, tf.float32)
    return ict


# Convert tensor to cube
def tensor_to_cube(tensor):
    cube = grids.E5sCube.copy()
    cube.data = tensor.numpy()
    return cube
