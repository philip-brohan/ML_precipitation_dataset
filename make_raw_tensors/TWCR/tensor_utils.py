# Utility functions for creating and manipulating raw tensors

import tensorflow as tf
import numpy as np

from get_data.TWCR import TWCR_monthly_load
from utilities import grids

rng = np.random.default_rng()


# Load the data for 1 month (on the standard cube).
def load_raw(year, month, member=None, variable="PRATE"):
    if member is None:
        member = rng.integers(low=1, high=80, size=1)
    raw = TWCR_monthly_load.load_monthly_member(
        variable=variable,
        year=year,
        month=month,
        member=member,
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
