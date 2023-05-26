#!/usr/bin/env python

# Get monthly GPCC in-situ precip for several years, and store on SCRATCH.

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=1891)
parser.add_argument("--endyear", type=int, required=False, default=2019)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
        opfile = "%s/GPCC/in-situ/monthly/precipitation/%04d/GPCC_total_precipitation_mon_0.25x0.25_global_%04d_v2020.0.nc" % (
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
