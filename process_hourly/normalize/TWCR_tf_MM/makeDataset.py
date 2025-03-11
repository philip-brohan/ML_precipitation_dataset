# Create raw data dataset for normalization

import os
import sys
import tensorflow as tf
import numpy as np
import zarr
import tensorstore as ts


# Get a dataset - all the tensors for a given and variable
def getDataset(
    variable,
    startyear=None,
    endyear=None,
    member_idx=None,
    year=None,
    month=None,
    day=None,
    hour=None,
    blur=None,
    cache=False,
):

    # Get the index of the last month in the raw tensors
    fn = "%s/MLP/raw_datasets_hourly/TWCR/%s_zarr" % (
        os.getenv("SCRATCH"),
        variable,
    )
    zarr_array = zarr.open(fn, mode="r")
    AvailableHours = zarr_array.attrs["AvailableHours"]
    dates = sorted(AvailableHours.keys())
    if startyear is not None:
        dates = [date for date in dates if int(date[:4]) >= startyear]
    if endyear is not None:
        dates = [date for date in dates if int(date[:4]) <= endyear]
    if year is not None:
        dates = [date for date in dates if int(date[:4]) == year]
    if month is not None:
        dates = [date for date in dates if int(date[5:7]) == month]
    if day is not None:
        dates = [date for date in dates if int(date[8:10]) == day]
    if hour is not None:
        dates = [date for date in dates if int(date[11:13]) == hour]
    if member_idx is not None:
        dates = [date for date in dates if int(date[-2:]) == member_idx]
    indices = [int(date[-2:]) * 1000000 + AvailableHours[date] for date in dates]

    # Create TensorFlow Dataset object from the source file dates
    tn_data = tf.data.Dataset.from_tensor_slices(tf.constant(dates, tf.string))
    ts_data = tf.data.Dataset.from_tensor_slices(tf.constant(indices, tf.int32))

    # Convert from list of available hours to Dataset of source file contents
    tsa = ts.open(
        {
            "driver": "zarr",
            "kvstore": "file://" + fn,
        }
    ).result()

    # Need the indirect function as zarr can't take tensor indices and .map prohibits .numpy()
    def load_tensor_from_index_py(idx):
        lidx = idx.numpy()
        m_idx = lidx // 1000000
        d_idx = lidx % 1000000
        return tf.convert_to_tensor(tsa[:, :, m_idx, d_idx].read().result(), tf.float32)

    def load_tensor_from_index(idx):
        result = tf.py_function(
            load_tensor_from_index_py,
            [idx],
            tf.float32,
        )
        result = tf.reshape(result, [256, 512, 1])
        return result

    ts_data = ts_data.map(
        load_tensor_from_index, num_parallel_calls=tf.data.experimental.AUTOTUNE
    )
    # Add noise to data - needed for some cases where the data is all zero
    if blur is not None:
        ts_data = ts_data.map(
            lambda x: x + tf.random.normal([256, 512, 1], stddev=blur),
            num_parallel_calls=tf.data.experimental.AUTOTUNE,
        )

    # Zip the data together with the years (so we can find the date and source of each
    #   data tensor if we need it).
    tz_data = tf.data.Dataset.zip((ts_data, tn_data))

    # Optimisation
    if cache:
        tz_data = tz_data.cache()  # Great, iff you have enough RAM for it

    tz_data = tz_data.prefetch(tf.data.experimental.AUTOTUNE)

    return tz_data
