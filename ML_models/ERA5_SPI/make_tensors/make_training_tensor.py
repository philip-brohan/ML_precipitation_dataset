#!/usr/bin/env python

# Read in monthly precip from ERA5
# Normalise: convert to normally distributed values on the range ~0-1
# Convert into a TensorFlow tensor.
# Serialise and store on $SCRATCH.

import os
import sys
import tensorflow as tf
import dask

# Going to do external parallelism - run this on one core
tf.config.threading.set_inter_op_parallelism_threads(1)
dask.config.set(scheduler="single-threaded")

import warnings

# warnings.filterwarnings("ignore", message=".*TransverseMercator.*")

# Where to store the tensors created
from ML_models.ERA5_SPI.localise import ModelName

from tensor_utils import load_raw, raw_to_tensor

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--test", help="test data, not training", action="store_true")
parser.add_argument(
    "--opfile", help="tf data file name", default=None, type=str, required=False
)
args = parser.parse_args()
if args.opfile is None:
    purpose = "training"
    if args.test:
        purpose = "test"
    args.opfile = ("%s/MLP/%s/datasets/%s/%04d-%02d.tfd") % (
        os.getenv("SCRATCH"),
        ModelName,
        purpose,
        args.year,
        args.month,
    )

if not os.path.isdir(os.path.dirname(args.opfile)):
    os.makedirs(os.path.dirname(args.opfile))

# Load and standardise data
qd = load_raw(args.year, args.month)
ict = raw_to_tensor(qd)

# Write to file
sict = tf.io.serialize_tensor(ict)
tf.io.write_file(args.opfile, sict)
