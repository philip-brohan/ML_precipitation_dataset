#!/usr/bin/env python

# Retrieve Copernicus station monthly accumulations.
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
    default="%s/Copernicus/land_surface_observations/monthly/precipitation/unrestricted"
    % os.getenv("SCRATCH"),
)
args = parser.parse_args()
args.opdir += "/%04d" % args.year
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)

for month in range(1, 13):
    ctrlB = {
        "format": "zip",
        "time_aggregation": "monthly",
        "variable": "accumulated_precipitation",
        "usage_restrictions": "unrestricted",
        "data_quality": "passed",
        "year": "%04d" % args.year,
        "month": "%02d" % month,
        "day": "01",
    }
    c = cdsapi.Client()

    c.retrieve(
        "insitu-observations-surface-land",
        ctrlB,
        "%s/download.zip" % args.opdir,
    )
    with zipfile.ZipFile("%s/download.zip" % args.opdir, "r") as zip_ref:
        zip_ref.extractall(args.opdir)
    os.remove("%s/download.zip" % args.opdir)
