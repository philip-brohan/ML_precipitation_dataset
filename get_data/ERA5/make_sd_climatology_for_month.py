#!/usr/bin/env python

# Make a sd climatology (1981-2010) for one month for one variable

import os
import iris
import iris.analysis.maths
import numpy as np
import argparse

from get_data.ERA5 import ERA5_monthly

parser = argparse.ArgumentParser()
parser.add_argument("--variable", help="Variable name", type=str, required=True)
parser.add_argument("--month", help="Month", type=int, required=True)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/ERA5/monthly/sd_climatology" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)

clim = ERA5_monthly.load_climatology(args.variable, args.month)

sum = None
count = 0
for year in range(1981, 2011):
    var = ERA5_monthly.load(args.variable, year, args.month)
    var = var - clim
    if sum is None:
        sum = var.copy()
        sum = sum * sum
    else:
        sum += var * var
    count += 1

sum /= count
sum.data[sum.data < 0] = 0  # Eliminates mising data issues
sum = iris.analysis.maths.apply_ufunc(np.sqrt, sum)

iris.save(sum, "%s/%s_%02d.nc" % (args.opdir, args.variable, args.month))
