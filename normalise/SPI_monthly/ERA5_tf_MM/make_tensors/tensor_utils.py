# Utility functions for creating and manipulating raw tensors

import os
import sys
import iris
import iris.cube
import iris.util
import iris.coords
import iris.coord_systems
import tensorflow as tf
import numpy as np

from get_data.ERA5 import ERA5_monthly
from utilities import grids

rng = np.random.default_rng()

import warnings

warnings.filterwarnings("ignore", message=".*datum.*")
warnings.filterwarnings("ignore", message=".*frac.*")


# Load the data for 1 month (on the standard cube).
def load_raw(year, month, member=None, variable="PRATE"):
    if member is None:
        member = rng.integers(low=1, high=80, size=1)
    raw = ERA5_monthly.load(
        variable=variable,
        year=year,
        month=month,
        grid=grids.E5sCube,
    )
    return raw


# Convert raw cube to tensor
def raw_to_tensor(raw):
    ict = tf.convert_to_tensor(raw.data, np.float32)
    return ict


# Convert tensor to cube
def tensor_to_cube(tensor):
    cube = grids.E5sCube.copy()
    cube.data = tensor.numpy()
    return cube