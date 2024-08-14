#!/usr/bin/env python

# Make normalized tensors

import os
import sys
import iris
import numpy as np
from shutil import rmtree
import zarr

# Supress iris moaning
# iris.FUTURE.save_split_attrs = True
iris.FUTURE.datum_support = True

# Supress TensorFlow moaning about cuda - we don't need a GPU for this
# Also the warning message confuses people.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
import tensorstore as ts
from normalize.SPI_monthly.CRU_tf_MM.makeDataset import getDataset
from normalize.SPI_monthly.CRU_tf_MM.normalize import match_normal, load_fitted


sDir = os.path.dirname(os.path.realpath(__file__))

# Get the date range from the input zarr array
fn = "%s/MLP/raw_datasets/CRU/in_situ/precipitation_zarr" % (os.getenv("SCRATCH"),)
input_zarr = zarr.open(fn, mode="r")
AvailableMonths = input_zarr.attrs["AvailableMonths"]


# Create the output zarr array
fn = "%s/MLP/normalized_datasets/CRU_tf_MM/precipitation_zarr" % (os.getenv("SCRATCH"),)
# Delete any previous version
if os.path.exists(fn):
    rmtree(fn)

normalized_zarr = ts.open(
    {
        "driver": "zarr",
        "kvstore": "file://" + fn,
    },
    dtype=ts.float32,
    chunk_layout=ts.ChunkLayout(chunk_shape=[721, 1440, 1]),
    create=True,
    fill_value=np.nan,
    shape=input_zarr.shape,
).result()
# Add date range to array as metadata
# TensorStore doesn't support metadata, so use the underlying zarr array
zarr_ds = zarr.open(fn, mode="r+")
zarr_ds.attrs["AvailableMonths"] = AvailableMonths

# Load the pre-calculated normalisation parameters
fitted = []
for month in range(1, 13):
    cubes = load_fitted(month)
    fitted.append([cubes[0].data, cubes[1].data, cubes[2].data])


# Go through raw dataset  and make normalized tensors
trainingData = getDataset(
    cache=False,
    blur=1.0e-9,
).batch(1)

op = []
for batch in trainingData:
    year = int(batch[1].numpy()[0][0:4])
    month = int(batch[1].numpy()[0][5:7])

    # normalize
    raw = batch[0].numpy().squeeze()
    normalized = match_normal(raw, fitted[month - 1])
    ict = tf.convert_to_tensor(normalized, tf.float32)
    tf.debugging.check_numerics(ict, "Bad data %04d-%02d" % (year, month))

    didx = AvailableMonths["%04d-%02d" % (year, month)]
    op.append(normalized_zarr[:, :, didx].write(ict))

# Ensure writes complete before exiting
for o in op:
    o.result()
