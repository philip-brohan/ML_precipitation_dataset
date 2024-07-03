#!/usr/bin/env python

# Get OCADA monthly data for several years, and store on SCRATCH.

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, default=1850)
parser.add_argument("--endyear", type=int, default=2015)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
    for var in [
        "ta",
        "slp",
        "precipi",
    ]:
        opfile = "%s/OCADA/monthly/means/%s_%04d.nc" % (
            os.getenv("SCRATCH"),
            var,
            year,
        )
        if not os.path.isfile(opfile):
            print(
                ("./get_year_of_monthlies.py --year=%d --variable=%s")
                % (
                    year,
                    var,
                )
            )
