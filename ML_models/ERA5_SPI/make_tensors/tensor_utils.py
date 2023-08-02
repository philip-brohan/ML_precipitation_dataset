# Utility functions for creating and manipulating tensors

import os
import sys
import iris
import iris.cube
import iris.util
import iris.coords
import iris.coord_systems
import tensorflow as tf
import numpy as np

from get_data import load_monthly
from normalise.SPI.ERA5.normalise import normalise_cube, unnormalise_cube, load_fitted

import warnings

warnings.filterwarnings("ignore", message=".*datum.*")
warnings.filterwarnings("ignore", message=".*frac.*")

# Define a standard-cube to work with
# Identical to that used in ERA5, except that the longitude cut is moved
#  to mid pacific (-180) instead of over the UK (0)
resolution = 0.25
xmin = -180
xmax = 180
ymin = -90
ymax = 90
pole_latitude = 90
pole_longitude = 180
npg_longitude = 0
cs = iris.coord_systems.RotatedGeogCS(pole_latitude, pole_longitude, npg_longitude)
lat_values = np.arange(ymin, ymax + resolution, resolution)
latitude = iris.coords.DimCoord(
    lat_values, standard_name="latitude", units="degrees_north", coord_system=cs
)
lon_values = np.arange(xmin, xmax + resolution, resolution)
longitude = iris.coords.DimCoord(
    lon_values, standard_name="longitude", units="degrees_east", coord_system=cs
)
dummy_data = np.zeros((len(lat_values), len(lon_values)))
sCube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

# Get fitted normalisation parameters and regrid to standard cube
(shape, location, scale) = load_fitted()
shape = shape.regrid(sCube, iris.analysis.Nearest())
location = location.regrid(sCube, iris.analysis.Nearest())
scale = scale.regrid(sCube, iris.analysis.Nearest())


# Load the data for 1 month and regrid to the standard cube.
def load_raw(year, month):
    raw = load_monthly.load(organisation="ERA5", year=year, month=month)
    raw = raw.regrid(sCube, iris.analysis.Nearest())
    return raw


# Normalise the data
def normalise(cube):
    return normalise_cube(cube, shape, location, scale)


def unnormalise(cube):
    return unnormalise_cube(cube, shape, location, scale)


# Convert raw cube to normalised tensor
def raw_to_tensor(raw):
    norm = normalise(raw)
    ict = tf.convert_to_tensor(norm.data, np.float32)
    return ict


# Convert normalised tensor to cube
def tensor_to_cube(tensor):
    cube = sCube.copy()
    cube.data = tensor.numpy()
    return cube


# Convert normalised tensor to raw precip
def tensor_to_raw(tensor):
    cube = tensor_to_cube(tensor)
    raw = unnormalise(cube)
    return raw
