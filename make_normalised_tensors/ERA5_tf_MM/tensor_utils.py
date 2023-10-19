# Utility functions for creating and manipulating normalised tensors

import tensorflow as tf

from get_data.ERA5 import ERA5_monthly
from utilities import grids
from normalise.SPI_monthly.ERA5_tf_MM.normalise import (
    normalise_cube,
    unnormalise_cube,
    load_fitted,
)

# Get fitted normalisation parameters
shape = []
location = []
scale = []
for month in range(1, 13):
    parameters = load_fitted(month)
    shape.append(parameters[0])
    location.append(parameters[1])
    scale.append(parameters[2])


# Load the data for 1 month
def load_raw(year, month, variable="total_precipitation"):
    raw = ERA5_monthly.load(
        variable=variable,
        year=year,
        month=month,
        grid=grids.E5sCube,
    )
    return raw


# Normalise the data
def normalise(cube, month):
    return normalise_cube(cube, shape[month - 1], location[month - 1], scale[month - 1])


def unnormalise(cube, month):
    return unnormalise_cube(
        cube, shape[month - 1], location[month - 1], scale[month - 1]
    )


# Convert raw cube to normalised tensor
def raw_to_tensor(raw, month):
    norm = normalise(raw, month)
    ict = tf.convert_to_tensor(norm.data, tf.float32)
    return ict


# Convert normalised tensor to cube
def tensor_to_cube(tensor):
    cube = grids.E5sCube.copy()
    cube.data = tensor.numpy()
    return cube


# Convert normalised tensor to raw values
def tensor_to_raw(tensor, month):
    cube = tensor_to_cube(tensor)
    raw = unnormalise(cube, month)
    return raw
