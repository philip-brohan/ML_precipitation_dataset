#!/usr/bin/env python

# Retrieve GPCC in-situ monthly averages.
#  Every month in one year

import os
import cdsapi
import argparse
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/GPCC/in-situ/monthly/precipitation" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
args.opdir += "/%04d" % args.year
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)


ctrlB = {
    "origin": "gpcc",
    "region": "global",
    "variable": "precipitation",
    "time_aggregation": "monthly",
    "horizontal_aggregation": "0_25_x_0_25",
    "year": "%04d" % args.year,
    "version": "v2020.0",
    "format": "zip",
}

c = cdsapi.Client()

c.retrieve(
    "insitu-gridded-observations-global-and-regional",
    ctrlB,
    "%s/download.zip" % args.opdir,
)
with zipfile.ZipFile("%s/download.zip" % args.opdir, "r") as zip_ref:
    zip_ref.extractall(args.opdir)
os.remove("%s/download.zip" % args.opdir)
