# Utility functions for creating and manipulating normalised tensors

import os
import sys
import iris
import iris.cube
import iris.util
import iris.coords
import iris.coord_systems
import tensorflow as tf
import numpy as np

from get_data.TWCR import TWCR_monthly_load
from utilities import grids

from normalise.SPI_monthly.TWCR_tf_MM.normalise import (
    load_fitted,
    normalise_cube,
    unnormalise_cube,
)

rng = np.random.default_rng()

import warnings

warnings.filterwarnings("ignore", message=".*datum.*")
warnings.filterwarnings("ignore", message=".*frac.*")


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
def raw_to_tensor(raw, variable, month):
    (shape, location, scale) = load_fitted(month, variable=variable)
    normalised = normalise_cube(raw, shape, location, scale)
    ict = tf.convert_to_tensor(normalised.data, np.float32)
    return ict


# Convert tensor to cube
def tensor_to_cube(tensor, variable, month):
    (shape, location, scale) = load_fitted(month, variable=variable)
    cube = grids.E5sCube.copy()
    cube.data = tensor.numpy()
    cube = unnormalise_cube(cube, shape, location, scale)
    return cube
