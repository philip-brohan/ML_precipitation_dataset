# Utility functions for creating and manipulating raw tensors

import numpy as np
import tensorflow as tf

from get_data.CRU.in_situ import CRU_i_monthly
from utilities import grids

rng = np.random.default_rng()

# Convert date into an array index
FirstYear = 1901
LastYear = 2019


def date_to_index(year, month):
    return (year - FirstYear) * 12 + month - 1


def index_to_date(idx):
    return (idx // 12) + FirstYear, (idx % 12) + 1


# Load the data for 1 month (on the standard cube)
def load_raw(year, month):
    raw = CRU_i_monthly.load(
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
