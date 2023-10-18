#!/usr/bin/env python

# Find optimum gamma parameters by fitting to the data moments

import os
import sys
import iris
from utilities import grids
import numpy as np
import tensorflow as tf

from makeDataset import getDataset

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--month", help="Month to fit", type=int, required=True)
parser.add_argument("--variable", help="Variable", type=str, required=True)
parser.add_argument(
    "--startyear", help="Start Year", type=int, required=False, default=1950
)
parser.add_argument(
    "--endyear", help="End Year", type=int, required=False, default=2014
)
parser.add_argument(
    "--member", help="Ensemble member", type=int, required=False, default=None
)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/MLP/normalisation/SPI_monthly/TWCR_tf_MM" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = "%s/%s" % (args.opdir, args.variable)
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)


# Go through data and estimate min and mean (for each month)
trainingData = getDataset(
    args.variable,
    startyear=args.startyear,
    endyear=args.endyear,
    cache=False,
    blur=1.0e-9,
).batch(1)
mean = tf.zeros([721, 1440, 1], dtype=tf.float32)
count = tf.zeros([1], dtype=tf.float32)
for batch in trainingData:
    month = int(batch[1].numpy()[0][5:7])
    if month == args.month:
        mean += batch[0][0, :, :, :] * 3
        count += 3.0
    if (
        month == args.month + 1
        or month == args.month - 1
        or (args.month == 1 and month == 12)
        or (args.month == 12 and month == 1)
    ):
        mean += batch[0][0, :, :, :]
        count += 1.0

mean /= count

# Go through again, now we know means, and estimate variance
variance = tf.zeros([721, 1440, 1], dtype=tf.float32)
for batch in trainingData:
    month = int(batch[1].numpy()[0][5:7])
    if month == args.month:
        variance += tf.math.squared_difference(batch[0][0, :, :, :], mean) * 3
    if (
        month == args.month + 1
        or month == args.month - 1
        or (args.month == 1 and month == 12)
        or (args.month == 12 and month == 1)
    ):
        variance += tf.math.squared_difference(batch[0][0, :, :, :], mean)

variance /= count

# Gamma parameter estimates:
fg_location = mean - tf.sqrt(variance) * 4
mean -= fg_location
fg_scale = variance / mean
fg_shape = mean / fg_scale

shape = grids.E5sCube.copy()
shape.data = np.squeeze(fg_shape.numpy())
iris.save(
    shape,
    "%s/%s/shape_m%02d.nc" % (args.opdir, args.variable, args.month),
)
location = grids.E5sCube.copy()
location.data = np.squeeze(fg_location.numpy())
iris.save(
    location,
    "%s/%s/location_m%02d.nc" % (args.opdir, args.variable, args.month),
)
scale = grids.E5sCube.copy()
scale.data = np.squeeze(fg_scale.numpy())
iris.save(
    scale,
    "%s/%s/scale_m%02d.nc" % (args.opdir, args.variable, args.month),
)
