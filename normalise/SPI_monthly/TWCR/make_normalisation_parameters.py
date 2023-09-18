#!/usr/bin/env python

# Get the gamma fit parameters needed for SPI normalisation

# This is slow, and extravagant in RAM usage, but with luck we won't need to run it often.

import os
import sys
import iris
import iris.cube
import iris.util
import iris.time
import numpy as np
import argparse
import pickle

from get_data.TWCR import TWCR_monthly_load

from scipy.stats import gamma

rng = np.random.default_rng()

parser = argparse.ArgumentParser()
parser.add_argument("--month", help="Month to fit", type=int, required=True)
parser.add_argument(
    "--startyear", help="First year of fit", type=int, required=False, default=1950
)
parser.add_argument(
    "--endyear", help="Last year of fit", type=int, required=False, default=2014
)
parser.add_argument(
    "--min_lat",
    help="Minimum latitude to extract",
    type=float,
    required=False,
    default=-90,
)
parser.add_argument(
    "--max_lat",
    help="Maximum latitude to extract",
    type=float,
    required=False,
    default=90.1,
)
parser.add_argument(
    "--variable",
    help="Name of variable to use (PRATE, TMP2m, PRMSL, ...)",
    type=str,
    default="PRATE",
)
parser.add_argument(
    "--member",
    help="Ensemble member to use. (Default, sample randomly)",
    type=int,
    default=None,
)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/MLP/normalisation/SPI_monthly/TWCR" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = "%s/%s" % (args.opdir, args.variable)
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)


llconstraint = iris.Constraint(
    coord_values={"latitude": lambda cell: args.min_lat <= cell < args.max_lat}
)
# Load the raw data
mp = args.month - 1
if mp < 1:
    mp = 12
mn = args.month + 1
if mn > 12:
    mn = 1
raw = iris.cube.CubeList()
for year in range(args.startyear, args.endyear + 1):
    for month in (mp, args.month, mn):
        member = args.member
        if member is None:
            member = rng.integers(low=1, high=80, size=1)
        m = TWCR_monthly_load.load_monthly_member(
            variable=args.variable,
            year=year,
            month=month,
            constraint=llconstraint,
            member=member,
        )
        m.cell_methods = None
        raw.append(m)

junk = iris.util.equalise_attributes(raw)
raw = raw.merge_cube()

# Make cubes to hold the fit parameters
# stime = iris.time.PartialDateTime(year=args.startyear, month=args.month)
shape = raw.extract(
    iris.Constraint(time=lambda cell: cell.point.year == args.startyear)
    & iris.Constraint(time=lambda cell: cell.point.month == args.month)
)
shape.data *= 0
location = shape.copy()
scale = shape.copy()
llshape = shape.data.shape
msub = raw.extract(iris.Constraint(time=lambda cell: cell.point.month == args.month))
mp = raw.extract(iris.Constraint(time=lambda cell: cell.point.month == mp))
mn = raw.extract(iris.Constraint(time=lambda cell: cell.point.month == mn))
for lat_i in range(llshape[0]):
    for lon_i in range(llshape[1]):
        fdata = msub.data[:, lat_i, lon_i]
        if lat_i > 0:
            fdata = np.append(fdata, msub.data[:, lat_i - 1, lon_i])
        if lon_i > 0:
            fdata = np.append(fdata, msub.data[:, lat_i, lon_i - 1])
        if lat_i < llshape[0] - 1:
            fdata = np.append(fdata, msub.data[:, lat_i + 1, lon_i])
        if lon_i < llshape[1] - 1:
            fdata = np.append(fdata, msub.data[:, lat_i, lon_i + 1])
        fdata = np.append(fdata, mp.data[:, lat_i, lon_i])
        fdata = np.append(fdata, mn.data[:, lat_i, lon_i])
        try:
            if args.variable == "PRATE":
                (
                    shape.data[lat_i, lon_i],
                    location.data[lat_i, lon_i],
                    scale.data[lat_i, lon_i],
                ) = gamma.fit(fdata, method="MLE", floc=-0.0001)
            else:
                (
                    shape.data[lat_i, lon_i],
                    location.data[lat_i, lon_i],
                    scale.data[lat_i, lon_i],
                ) = gamma.fit(fdata, method="MLE")
        except Exception:
            print("Failed for %d %d %d" % (month, lat_i, lon_i))
        if np.isnan(shape.data[lat_i, lon_i]):
            # This means that all the data is zero - replace with nominal distn
            (
                shape.data[lat_i, lon_i],
                location.data[lat_i, lon_i],
                scale.data[lat_i, lon_i],
            ) = (0.88, -0.0001, 0.0006)
        if np.isnan(location.data[lat_i, lon_i]):
            raise Exception("Bad location %d %d %d" % (lat_i, lon_i, args.month))
        if np.isnan(scale.data[lat_i, lon_i]):
            with open("tmp.pkl", "wb") as opf:
                pickle.dump((fdata), opf)
            raise Exception("Bad scale %d %d %d" % (lat_i, lon_i, args.month))

iris.save(
    shape,
    "%s/%s/shape_m%02d_%03d_%03d.nc"
    % (args.opdir, args.variable, args.month, int(args.min_lat), int(args.max_lat)),
)
iris.save(
    location,
    "%s/%s/location_m%02d_%03d_%03d.nc"
    % (args.opdir, args.variable, args.month, int(args.min_lat), int(args.max_lat)),
)
iris.save(
    scale,
    "%s/%s/scale_m%02d_%03d_%03d.nc"
    % (args.opdir, args.variable, args.month, int(args.min_lat), int(args.max_lat)),
)
