#!/usr/bin/env python

# Time series validation is a bit slow - run it in parallel
# This script prints out a series of scripts to be run on SPICE


import os

opdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--mlabel",
    type=str,
    required=False,
    default=None,
)
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
parser.add_argument(
    "--start_year",
    type=int,
    required=False,
    default=1850,
)
parser.add_argument(
    "--end_year",
    type=int,
    required=False,
    default=2023,
)
parser.add_argument(
    "--label",  # name for this validation run
    type=str,
    required=True,
    default=None,
)
args = parser.parse_args()

for year in range(args.start_year,args.end_year+1):
    print("./validate_time_series.py --start_year=%04d --end_year=%04d --label=%s " % (year,year,args.label), end="")
    if args.mlabel is not None:
        print("--mlabel=%s" % args.mlabel, end="")
    if args.no_pressure:
        print("--no_pressure ", end="")
    if args.no_temperature:
        print("--no_temperature ", end="")
    if args.fix_month is not None:
        print("--fix_month=%s" % args.fix_month, end="")
    if args.fix_lat is not None:
        print("--fix_lat=%s" % args.fix_lat, end="")
    if args.fix_lon is not None:
        print("--fix_lon=%s" % args.fix_lon, end="")
    print("") # add \n
