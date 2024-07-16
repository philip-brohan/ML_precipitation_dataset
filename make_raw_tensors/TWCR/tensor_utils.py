# Utility functions for creating and manipulating raw tensors

import numpy as np
import tensorflow as tf

from get_data.TWCR import TWCR_monthly_load
from utilities import grids

rng = np.random.default_rng()

# Convert date into an array index
FirstYear = 1850
LastYear = 2014


def date_to_index(year, month):
    return (year - FirstYear) * 12 + month - 1


def index_to_date(idx):
    return (idx // 12) + FirstYear, (idx % 12) + 1


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
