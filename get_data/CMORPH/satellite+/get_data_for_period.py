#!/usr/bin/env python

# Get monthly CMORPH adjusted satellite precip for several years, and store on SCRATCH.

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=1998)
parser.add_argument("--endyear", type=int, required=False, default=2021)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
        opfile = "%s/CMORPH/satellite+/monthly/precipitation/%04d/CMORPH_total_precipitation_mon_0.5x0.5_quasi-global_%04d_v1.0.nc" % (
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
