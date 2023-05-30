#!/usr/bin/env python

# Retrieve GPCC satellite monthly averages.
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
    default="%s/GPCC/satellite+gauge/monthly/precipitation" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
args.opdir += "/%04d" % args.year
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)


ctrlB = {
        'variable': 'all',
        'time_aggregation': 'monthly_mean',
        'year': "%04d" % args.year,
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'format': 'zip',
    }

c = cdsapi.Client()

c.retrieve(
    "satellite-precipitation",
    ctrlB,
    "%s/download.zip" % args.opdir,
)
with zipfile.ZipFile("%s/download.zip" % args.opdir, 'r') as zip_ref:
    zip_ref.extractall(args.opdir)
os.remove("%s/download.zip" % args.opdir)