#!/usr/bin/env python

# Get monthly Copernicus satellite microwave precip for several years, and store on SCRATCH.

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=2000)
parser.add_argument("--endyear", type=int, required=False, default=2017)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
        opfile = "%s/Copernicus/satellite_microwave/monthly/precipitation/%04d/COBRA_%04d-01_1DM_v1.0.nc" % (
            os.getenv("SCRATCH"),
            year,
            year,
        )
        if not os.path.isfile(opfile):
            print(
                ("./get_year_of_monthlies.py --year=%d")
                % (
                    year,
                )
            )
