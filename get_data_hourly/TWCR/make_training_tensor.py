#!/usr/bin/env python

# Read in monthly variable from TWCR - regrid to model resolution
# Convert into a TensorFlow tensor.
# Serialise and store on $SCRATCH.

import os
import sys
import numpy as np
import warnings
from get_data.TWCR import TWCR_monthly_load

# Supress TensorFlow moaning about cuda - we don't need a GPU for this
# Also the warning message confuses people.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
import tensorstore as ts

import dask

# Going to do external parallelism - run this on one core
tf.config.threading.set_inter_op_parallelism_threads(1)
dask.config.set(scheduler="single-threaded")

from tensor_utils import load_raw, raw_to_tensor, date_to_index

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument(
    "--member_idx", help="Ensemble member index (0-9)", type=int, required=True
)
parser.add_argument("--variable", help="Variable name", type=str, required=True)
args = parser.parse_args()

fn = "%s/MLP/raw_datasets/TWCR/%s_zarr" % (
    os.getenv("SCRATCH"),
    args.variable,
)

dataset = ts.open(
    {
        "driver": "zarr",
        "kvstore": "file://" + fn,
    }
).result()

# Load and standardise data
try:
    qd = load_raw(
        args.year,
        args.month,
        member=TWCR_monthly_load.members[args.member_idx],
        variable=args.variable,
    )
    ict = raw_to_tensor(qd)
except Exception:
    warnings.warn(
        "Failed to load data for %s %04d-%02d" % (args.variable, args.year, args.month)
    )
    ict = tf.fill([721, 1440], tf.constant(np.nan, dtype=tf.float32))

# Write to file
didx = date_to_index(args.year, args.month)
midx = args.member_idx
op = dataset[:, :, midx, didx].write(ict)
op.result()  # Ensure write completes before exiting
