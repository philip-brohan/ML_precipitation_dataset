#!/usr/bin/env python

# Find optimum gamma parameters by fitting to the data moments

import os
import sys
import iris
from utilities import grids
import numpy as np

# Supress TensorFlow moaning about cuda - we don't need a GPU for this
# Also the warning message confuses people.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf

from makeDataset import getDataset

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--month", help="Month to fit", type=int, required=True)
parser.add_argument("--day", help="Day to fit", type=int, required=True)
parser.add_argument("--hour", help="Hour to fit", type=int, required=True)
parser.add_argument("--variable", help="Variable", type=str, required=True)
parser.add_argument(
    "--startyear", help="Start Year", type=int, required=False, default=1950
)
parser.add_argument(
    "--endyear", help="End Year", type=int, required=False, default=2014
)
parser.add_argument(
    "--memberidx", help="Member index (0-9)", type=int, required=False, default=None
)

parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/MLP/normalization/SPI_hourly/TWCR_tf_MM" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = "%s/%s" % (args.opdir, args.variable)
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)


# Go through data and estimate min and mean (for each hour)
trainingData = getDataset(
    args.variable,
    startyear=args.startyear,
    endyear=args.endyear,
    month=args.month,
    day=args.day,
    hour=args.hour,
    member_idx=args.memberidx,
    cache=False,
    blur=1.0e-9,
).batch(1)
mean = tf.zeros([1, 256, 512, 1], dtype=tf.float32)
count = tf.zeros([1, 256, 512, 1], dtype=tf.float32)
for batch in trainingData:
    month = int(batch[1].numpy()[0][5:7])
    day = int(batch[1].numpy()[0][8:10])
    hour = int(batch[1].numpy()[0][11:13])
    if month == args.month and day == args.day and hour == args.hour:
        valid = ~tf.math.is_nan(batch[0])
        mean = tf.where(valid, mean + batch[0], mean)
        count = tf.where(valid, count + 1, count)

enough = count >= 10
mean = tf.where(enough, mean / count, np.nan)

count *= 0
# Go through again, now we know means, and estimate variance
variance = tf.zeros([256, 512, 1], dtype=tf.float32)
for batch in trainingData:
    month = int(batch[1].numpy()[0][5:7])
    day = int(batch[1].numpy()[0][8:10])
    hour = int(batch[1].numpy()[0][11:13])
    if month == args.month and day == args.day and hour == args.hour:
        valid = tf.math.logical_and(~tf.math.is_nan(batch[0]), ~tf.math.is_nan(mean))
        variance = tf.where(
            valid, variance + tf.math.squared_difference(batch[0], mean), variance
        )
        count = tf.where(valid, count + 1.0, count)

enough = count >= 10
variance = tf.where(enough, variance / count, np.nan)

# Artificially expand under-sea-ice variability in SST
if args.variable == "SST":
    variance = tf.where(np.logical_and(enough, mean < 273), variance + 0.5, variance)

# Gamma parameter estimates:
fg_location = tf.zeros([1, 256, 512, 1], dtype=tf.float32)
fg_location = tf.where(enough, mean - tf.sqrt(variance) * 4, np.nan)
mean = tf.where(enough, mean - fg_location, np.nan)
fg_scale = tf.where(enough, variance / mean, np.nan)
fg_shape = tf.where(enough, mean / fg_scale, np.nan)

shape = grids.TWCRCube.copy()
shape.data = np.squeeze(fg_shape.numpy())
shape.data = np.ma.MaskedArray(shape.data, np.isnan(shape.data))
shape.data.data[shape.data.mask] = 1.0
iris.save(
    shape,
    "%s/%s/shape_m%02d_d%02d_h%02d.nc"
    % (args.opdir, args.variable, args.month, args.day, args.hour),
)
location = grids.TWCRCube.copy()
location.data = np.squeeze(fg_location.numpy())
location.data = np.ma.MaskedArray(location.data, np.isnan(location.data))
location.data.data[location.data.mask] = -1.0
iris.save(
    location,
    "%s/%s/location_m%02d_d%02d_h%02d.nc"
    % (args.opdir, args.variable, args.month, args.day, args.hour),
)
scale = grids.TWCRCube.copy()
scale.data = np.squeeze(fg_scale.numpy())
scale.data = np.ma.MaskedArray(scale.data, np.isnan(scale.data))
scale.data.data[scale.data.mask] = 1.0
iris.save(
    scale,
    "%s/%s/scale_m%02d_d%02d_h%02d.nc"
    % (args.opdir, args.variable, args.month, args.day, args.hour),
)
