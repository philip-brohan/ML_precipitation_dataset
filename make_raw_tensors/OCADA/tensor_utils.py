# Utility functions for creating and manipulating raw tensors

import numpy as np
import tensorflow as tf

from get_data.OCADA import OCADA_monthly_load
from utilities import grids


# Load the data for 1 month (on the standard cube).
def load_raw(year, month, variable="precipi"):
    raw = OCADA_monthly_load.load_monthly(
        variable=variable,
        year=year,
        month=month,
        grid=grids.E5sCube,
    )
    if np.ma.is_masked(raw.data):
        raw.data.data[raw.data.mask == True] = np.nan
    return raw


# Convert raw cube to tensor
def raw_to_tensor(raw):
    ict = tf.convert_to_tensor(raw.data, tf.float32)
    return ict


# Convert tensor to cube
def tensor_to_cube(tensor):
    cube = grids.E5sCube.copy()
    cube.data = tensor.numpy()
    cube.data = np.ma.MaskedArray(cube.data, np.isnan(cube.data))
    return cube
