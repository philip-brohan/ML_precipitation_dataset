#!/usr/bin/env python

# Make normalized tensors

import os
import sys
import argparse
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
from process_hourly.normalize.TWCR_tf_MM.makeDataset import getDataset
from process_hourly.normalize.TWCR_tf_MM.normalize import match_normal, load_fitted

sDir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--variable",
    help="Variable name",
    type=str,
    required=True,
)
parser.add_argument(
    "--month",
    help="Restrict to selected month",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--day",
    help="Restrict to selected day of month",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--hour",
    help="Restrict to selected hour of day",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--delete",
    help="Delete existing zarr array",
    action="store_true",
)
args = parser.parse_args()

# Get the date range from the input zarr array
fn = "%s/MLP/raw_datasets_hourly/TWCR/%s_zarr" % (
    os.getenv("SCRATCH"),
    args.variable,
)
input_zarr = zarr.open(fn, mode="r")
AvailableHours = input_zarr.attrs["AvailableHours"]


# Create the output zarr array
fn = "%s/MLP/normalized_datasets_hourly/TWCR_tf_MM/%s_zarr" % (
    os.getenv("SCRATCH"),
    args.variable,
)

if args.delete:
    # Delete any previous version
    if os.path.exists(fn):
        rmtree(fn)

    normalized_zarr = ts.open(
        {
            "driver": "zarr",
            "kvstore": "file://" + fn,
        },
        dtype=ts.float32,
        chunk_layout=ts.ChunkLayout(chunk_shape=[256, 512, 1, 1]),
        create=True,
        fill_value=np.nan,
        shape=input_zarr.shape,
    ).result()
    # Add date range to array as metadata
    # TensorStore doesn't support metadata, so use the underlying zarr array
    zarr_ds = zarr.open(fn, mode="r+")
    zarr_ds.attrs["AvailableHours"] = AvailableHours
else:
    normalized_zarr = ts.open(
        {
            "driver": "zarr",
            "kvstore": "file://" + fn,
        },
    ).result()
# Load the pre-calculated normalisation parameters
fitted = {}
for month in range(1, 13):
    if args.month is not None and month != args.month:
        continue
    for day in range(1, 32):
        if args.day is not None and day != args.day:
            continue
        for hour in range(0, 24, 3):
            if args.hour is not None and hour != args.hour:
                continue
            try:
                cubes = load_fitted(month, day, hour, variable=args.variable)
                fitted["%02d-%02d_%02d" % (month, day, hour)] = [
                    cubes[0].data,
                    cubes[1].data,
                    cubes[2].data,
                ]
            except Exception as e:
                pass

# Go through raw dataset  and make normalized tensors
trainingData = getDataset(
    args.variable,
    month=args.month,
    day=args.day,
    hour=args.hour,
    cache=False,
    blur=1.0e-9,
).batch(1)

op = []
for batch in trainingData:
    year = int(batch[1].numpy()[0][0:4])
    month = int(batch[1].numpy()[0][5:7])
    day = int(batch[1].numpy()[0][8:10])
    hour = int(batch[1].numpy()[0][11:13])
    member_idx = int(batch[1].numpy()[0][-2:])

    # normalize
    raw = batch[0].numpy().squeeze()
    normalized = match_normal(raw, fitted["%02d-%02d_%02d" % (month, day, hour)])
    ict = tf.convert_to_tensor(normalized, tf.float32)
    tf.debugging.check_numerics(
        ict, "Bad data %04d-%02d-%02d:%02d %02d" % (year, month, day, hour, member_idx)
    )

    didx = AvailableHours[
        "%04d-%02d-%02d:%02d_%02d" % (year, month, day, hour, member_idx)
    ]
    op.append(normalized_zarr[:, :, member_idx, didx].write(ict))

# Ensure writes complete before exiting
for o in op:
    o.result()
