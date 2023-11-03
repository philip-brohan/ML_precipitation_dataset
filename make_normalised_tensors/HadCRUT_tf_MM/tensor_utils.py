# Utility functions for creating and manipulating normalised tensors

import tensorflow as tf
import numpy as np

from get_data.HadCRUT import HadCRUT
from utilities import grids

from normalise.SPI_monthly.HadCRUT_tf_MM.normalise import (
    load_fitted,
    normalise_cube,
    unnormalise_cube,
)

rng = np.random.default_rng()


# Load the data for 1 month (on the standard cube).
def load_raw(year, month, member=None):
    if member is None:
        member = HadCRUT.members[rng.integers(low=0, high=len(members), size=1)]
    raw = HadCRUT.load(
        year=year,
        month=month,
        member=member,
        grid=grids.E5sCube,
    )
    raw.data.data[raw.data.mask == True] = 0.0
    return raw


# Convert raw cube to tensor
def raw_to_tensor(raw, month):
    (shape, location, scale) = load_fitted(month)
    norm = normalise_cube(raw, shape, location, scale)
    norm.data.data[raw.data.mask == True] = 0.0
    ict = tf.convert_to_tensor(norm.data, tf.float32)
    return ict


# Convert normalised tensor to cube
def tensor_to_cube(tensor):
    cube = grids.E5sCube.copy()
    cube.data = tensor.numpy()
    cube.data = np.ma.MaskedArray(cube.data, cube.data == 0.0)
    return cube


# Convert normalised tensor to raw values
def tensor_to_raw(tensor, variable, month):
    (shape, location, scale) = load_fitted(month, variable=variable)
    cube = tensor_to_cube(tensor)
    raw = unnormalise_cube(cube, shape, location, scale)
    raw.data.data[raw.data.mask == True] = 0.0
    return raw
