#!/usr/bin/env python

# Get the gamma fit parameters needed for SPI normalization

# This is slow, and extravagant in RAM usage, but with luck we won't need to run it often.

import os
import sys
import iris
import iris.cube
import iris.util
import iris.time
import numpy as np
import argparse

from get_data import load_monthly

from scipy.stats import gamma

parser = argparse.ArgumentParser()
parser.add_argument(
    "--startyear", help="First year of fit", type=int, required=False, default=1940
)
parser.add_argument(
    "--endyear", help="Last year of fit", type=int, required=False, default=2020
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
    "--opdir",
    help="Directory for output files",
    default="%s/MLP/normalization/SPI/ERA5" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)


llconstraint = iris.Constraint(
    coord_values={"latitude": lambda cell: args.min_lat <= cell < args.max_lat}
)
# Load the raw data
raw = iris.cube.CubeList()
for year in range(args.startyear, args.endyear + 1):
    for month in range(1, 13):
        m = load_monthly.load(
            organisation="ERA5", year=year, month=month, constraint=llconstraint
        )
        raw.append(m)

junk = iris.util.equalise_attributes(raw)
raw = raw.merge_cube()

# Make cubes to hold the fit parameters
stime = iris.time.PartialDateTime(year=args.startyear, month=1, day=1, hour=0)
shape = raw.extract(iris.Constraint(time=stime))
shape.data *= 0
location = shape.copy()
scale = shape.copy()
llshape = shape.data.shape
for lat_i in range(llshape[0]):
    for lon_i in range(llshape[1]):
        try:
            (
                shape.data[lat_i, lon_i],
                location.data[lat_i, lon_i],
                scale.data[lat_i, lon_i],
            ) = gamma.fit(np.cbrt(raw.data[:, lat_i, lon_i]),method='MM')
        except Exception:
            print("Failed for %d %d" % (lat_i, lon_i))

iris.save(
    shape, "%s/shape_%03d_%03d.nc" % (args.opdir, int(args.min_lat), int(args.max_lat))
)
iris.save(
    location,
    "%s/location_%03d_%03d.nc" % (args.opdir, int(args.min_lat), int(args.max_lat)),
)
iris.save(
    scale, "%s/scale_%03d_%03d.nc" % (args.opdir, int(args.min_lat), int(args.max_lat))
)
