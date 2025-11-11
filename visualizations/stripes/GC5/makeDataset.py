# Create normalized dataset

import os
import sys
import tensorflow as tf
import numpy as np
import zarr
import tensorstore as ts


# Get a full dataset - all three runs one after the other
def getDataset(
    variable,
    startyear=None,
    endyear=None,
    blur=None,
    cache=False,
    prefetch=True,
):
    ds1 = getrunDataset(
        "dl339",
        variable,
        startyear=startyear,
        endyear=endyear,
        blur=blur,
        cache=False,
        prefetch=False,
    )
    ds1 = ds1.concatenate(
        getrunDataset(
            "dl340",
            variable,
            startyear=startyear,
            endyear=endyear,
            blur=blur,
            cache=False,
            prefetch=False,
        )
    )
    ds1 = ds1.concatenate(
        getrunDataset(
            "dl341",
            variable,
            startyear=startyear,
            endyear=endyear,
            blur=blur,
            cache=False,
            prefetch=False,
        )
    )

    # Optimisation
    if cache:
        ds1 = ds1.cache()  # Great, iff you have enough RAM for it

    if prefetch:
        ds1 = ds1.prefetch(tf.data.experimental.AUTOTUNE)

    return ds1


# Get a run dataset - all the tensors for a given run and variable
def getrunDataset(
    run,
    variable,
    startyear=None,
    endyear=None,
    blur=None,
    cache=False,
    prefetch=False,
):

    # Get the index of the last month in the normalized tensors
    fn = "%s/normalized_datasets/GC5_tf_MM/historical/%s/%s_zarr" % (
        os.getenv("PDIR"),
        run,
        variable,
    )
    zarr_array = zarr.open(fn, mode="r")
    AvailableMonths = zarr_array.attrs["AvailableMonths"]
    dates = sorted(AvailableMonths.keys())
    if startyear is not None:
        dates = [date for date in dates if int(date[:4]) >= startyear]
    if endyear is not None:
        dates = [date for date in dates if int(date[:4]) <= endyear]
    indices = [AvailableMonths[date] for date in dates]
    # Will use dates as tensor labels, so need to append run to identify that
    dates_run = [date + "_" + run for date in dates]

    # Create TensorFlow Dataset object from the source file dates
    tn_data = tf.data.Dataset.from_tensor_slices(tf.constant(dates_run, tf.string))
    ts_data = tf.data.Dataset.from_tensor_slices(tf.constant(indices, tf.int32))

    # Convert from list of available months to Dataset of source file contents
    tsa = ts.open(
        {
            "driver": "zarr",
            "kvstore": "file://" + fn,
        }
    ).result()

    # Need the indirect function as zarr can't take tensor indices and .map prohibits .numpy()
    def load_tensor_from_index_py(idx):
        return tf.convert_to_tensor(tsa[:, :, idx.numpy()].read().result(), tf.float32)

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

    if prefetch:
        tz_data = tz_data.prefetch(tf.data.experimental.AUTOTUNE)

    return tz_data
