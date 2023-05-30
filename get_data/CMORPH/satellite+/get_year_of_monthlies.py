#!/usr/bin/env python

# Retrieve CMORPH adjusted satellite monthly averages.
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
    default="%s/CMORPH/satellite+/monthly/precipitation" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
args.opdir += "/%04d" % args.year
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)


ctrlB = {
        'format': 'zip',
        'origin': 'cmorph',
        'variable': 'precipitation',
        'region': 'quasi_global',
        'time_aggregation': 'monthly',
        'horizontal_aggregation': '0_5_x_0_5',
        'version': 'v1.0',
        'year': "%04d" % args.year,
    }

c = cdsapi.Client()

c.retrieve(
    "insitu-gridded-observations-global-and-regional",
    ctrlB,
    "%s/download.zip" % args.opdir,
)
with zipfile.ZipFile("%s/download.zip" % args.opdir, 'r') as zip_ref:
    zip_ref.extractall(args.opdir)
os.remove("%s/download.zip" % args.opdir)