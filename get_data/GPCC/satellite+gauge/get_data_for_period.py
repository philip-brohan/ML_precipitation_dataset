#!/usr/bin/env python

# Get monthly GPCC satellite+gauge precip for several years, and store on SCRATCH.

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=1979)
parser.add_argument("--endyear", type=int, required=False, default=2022)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
        opfile = "%s/GPCC/satellite+gauge/monthly/precipitation/%04d/gpcp_v02r03_monthly_d%04d01.nc" % (
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
