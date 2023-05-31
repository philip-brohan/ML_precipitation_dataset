#!/usr/bin/env python

# Make a climatology (1981-2010) for one month for one variable

import os
import iris
import argparse

from get_data.ERA5 import ERA5_monthly

parser = argparse.ArgumentParser()
parser.add_argument("--variable", help="Variable name", type=str, required=True)
parser.add_argument("--month", help="Month", type=int, required=True)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/ERA5/monthly/climatology" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)

sum = None
count = 0
for year in range(1981, 2011):
    var = ERA5_monthly.load(args.variable, year=year, month=args.month)
    if sum is None:
        sum = var.copy()
    else:
        sum += var
    count += 1

sum /= count

iris.save(sum, "%s/%s_%02d.nc" % (args.opdir, args.variable, args.month))
