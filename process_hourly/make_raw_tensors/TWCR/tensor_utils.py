# Utility functions for creating and manipulating raw tensors

import numpy as np
import tensorflow as tf
import datetime

from get_data_hourly.TWCR import TWCR_hourly_load
from utilities import grids

rng = np.random.default_rng()

# Convert date into an array index
FirstYear = datetime.datetime(1850, 1, 1, 0)
LastYear = datetime.datetime(2014, 12, 31, 21)


def date_to_index(year, month, day, hour):
    sdiff = datetime.datetime(year, month, day, hour) - FirstYear
    return int(sdiff.total_seconds() // (3600 * 3))


def index_to_date(idx):
    ddif = datetime.timedelta(seconds=idx * 3 * 3600)
    return FirstYear + ddif


# Load the data for 1 month (on the standard cube).
def load_raw(year, month, day, hour, member=None, variable="PRATE"):
    if member is None:
        member = rng.integers(low=1, high=80, size=1)
    raw = TWCR_hourly_load.load_hourly_member(
        variable=variable,
        year=year,
        month=month,
        day=day,
        hour=hour,
        member=member,
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
    cube = grids.TWCRCube.copy()
    cube.data = tensor.numpy()
    cube.data = np.ma.MaskedArray(cube.data, np.isnan(cube.data))
    return cube
