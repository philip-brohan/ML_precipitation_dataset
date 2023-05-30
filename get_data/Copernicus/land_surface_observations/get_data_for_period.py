#!/usr/bin/env python

# Get monthly Copernicus in-situ precip observations for several years, and store on SCRATCH.

import os
import argparse
import glob

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=1901)
parser.add_argument("--endyear", type=int, required=False, default=2020)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
    opfile_c = len(
        glob.glob(
            "%s/Copernicus/land_surface_observations/monthly/precipitation/unrestricted/%04d/*.csv"
            % (
                os.getenv("SCRATCH"),
                year,
            )
        )
    )
    if opfile_c < 12:
        print(("./get_year_of_monthlies.py --year=%d") % (year,))
