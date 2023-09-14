#!/usr/bin/env python

# Get monthly 20CRv3 members  data for several years, and store on SCRATCH.

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, default=1850)
parser.add_argument("--endyear", type=int, default=2014)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
    for var in [
        "TMPS",
        "TMP2m",
        "PRMSL",
        "PRATE",
    ]:
        opfile = "%s/20CR/version_3/monthly/members/%04d/%s.%04d.mnmean_mem080.nc" % (
            os.getenv("SCRATCH"),
            year,
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
