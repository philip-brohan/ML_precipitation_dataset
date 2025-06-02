#!/usr/bin/env python

# Check the fits for the normalization parameters
#  mising files and bad values

import os
import iris
import iris.time

iris.FUTURE.datum_support = True
import numpy as np

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--month", help="Month to plot", type=int, required=False, default=None
)
parser.add_argument("--day", help="Day to plot", type=int, required=False, default=None)
parser.add_argument(
    "--hour", help="Hour to plot", type=int, required=False, default=None
)
parser.add_argument(
    "--variable",
    help="Name of variable to use (PRATE, TMP2m, PRMSL, ...)",
    type=str,
    default="PRATE",
)
args = parser.parse_args()

for month in range(1, 13):
    if args.month is not None and month != args.month:
        continue
    for day in range(1, 32):
        if args.day is not None and day != args.day:
            continue
        if month == 2 and day > 28:
            continue
        for hour in range(0, 24, 3):
            if args.hour is not None and hour != args.hour:
                continue
            try:
                dte = datetime.datetime(1961, month, day, hour)
            except Exception as e:  # Some months have fewer than 31 days
                continue
            try:
                shape = iris.load_cube(
                    "%s/MLP/normalization/SPI_hourly/TWCR_tf_MM/%s/shape_m%02d_d%02d_h%02d.nc"
                    % (
                        os.getenv("PDIR"),
                        args.variable,
                        month,
                        day,
                        hour,
                    ),
                )
            except Exception as e:
                print(
                    "Missing shape file for %s %02d-%02d:%02d"
                    % (args.variable, month, day, hour)
                )
                continue
            if np.any(np.isnan(shape.data)):
                print(
                    "Bad shape file for %s %02d-%02d:%02d"
                    % (args.variable, month, day, hour)
                )
            try:
                location = iris.load_cube(
                    "%s/MLP/normalization/SPI_hourly/TWCR_tf_MM/%s/location_m%02d_d%02d_h%02d.nc"
                    % (
                        os.getenv("PDIR"),
                        args.variable,
                        month,
                        day,
                        hour,
                    ),
                )
            except Exception as e:
                print(
                    "Missing location file for %s %02d-%02d:%02d"
                    % (args.variable, month, day, hour)
                )
                continue
            if np.any(np.isnan(location.data)):
                print(
                    "Bad location file for %s %02d-%02d:%02d"
                    % (args.variable, month, day, hour)
                )
            try:
                scale = iris.load_cube(
                    "%s/MLP/normalization/SPI_hourly/TWCR_tf_MM/%s/scale_m%02d_d%02d_h%02d.nc"
                    % (
                        os.getenv("PDIR"),
                        args.variable,
                        month,
                        day,
                        hour,
                    ),
                )
            except Exception as e:
                print(
                    "Missing scale file for %s %02d-%02d:%02d"
                    % (args.variable, month, day, hour)
                )
                continue
            if np.any(np.isnan(scale.data)):
                print(
                    "Bad scale file for %s %02d-%02d:%02d"
                    % (args.variable, month, day, hour)
                )
