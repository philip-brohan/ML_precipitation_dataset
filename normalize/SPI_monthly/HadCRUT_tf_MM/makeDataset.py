# Create raw data dataset for normalization

import os
import sys
import tensorflow as tf
import numpy as np
import zarr
import tensorstore as ts


# Get a dataset - all the tensors for a given and variable
def getDataset(
    startyear=None,
    endyear=None,
    member_idx=None,
    blur=None,
    cache=False,
):

    # Get the index of the last month in the raw tensors
    fn = "%s/MLP/raw_datasets/HadCRUT/temperature_zarr" % (os.getenv("SCRATCH"),)
    zarr_array = zarr.open(fn, mode="r")
    AvailableMonths = zarr_array.attrs["AvailableMonths"]
    dates = sorted(AvailableMonths.keys())
    if startyear is not None:
        dates = [date for date in dates if int(date[:4]) >= startyear]
    if endyear is not None:
        dates = [date for date in dates if int(date[:4]) <= endyear]
    if member_idx is not None:
        dates = [date for date in dates if int(date[-2:]) == member_idx]
    # index = member_idx*10000 + month_idx
    indices = [int(date[-2:]) * 10000 + AvailableMonths[date] for date in dates]

    # Create TensorFlow Dataset object from the source file dates
    tn_data = tf.data.Dataset.from_tensor_slices(tf.constant(dates, tf.string))
    ts_data = tf.data.Dataset.from_tensor_slices(tf.constant(indices, tf.int32))

    # Convert from list ofavailable months to Dataset of source file contents
    tsa = ts.open(
        {
            "driver": "zarr",
            "kvstore": "file://" + fn,
        }
    ).result()

    # Need the indirect function as zarr can't take tensor indices and .map prohibits .numpy()
    def load_tensor_from_index_py(idx):
        lidx = idx.numpy()
        m_idx = lidx // 10000
        d_idx = lidx % 10000
        return tf.convert_to_tensor(tsa[:, :, m_idx, d_idx].read().result(), tf.float32)

    def load_tensor_from_index(idx):
        result = tf.py_function(
            load_tensor_from_index_py,
            [idx],
            tf.float32,
        )
        result = tf.reshape(result, [721, 1440, 1])
        return result

    ts_data = ts_data.map(
        load_tensor_from_index, num_parallel_calls=tf.data.experimental.AUTOTUNE
    )
    # Add noise to data - needed for some cases where the data is all zero
    if blur is not None:
        ts_data = ts_data.map(
            lambda x: x + tf.random.normal([721, 1440, 1], stddev=blur),
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
