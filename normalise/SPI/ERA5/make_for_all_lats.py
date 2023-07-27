#!/usr/bin/env python

# Normalise the ERA5 data for all latitude bands

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=1940)
parser.add_argument("--endyear", type=int, required=False, default=2022)
args = parser.parse_args()

for max_lat in range(-89, 91):
    opfile = "%s/MLP/normalisation/SPI/ERA5/shape_%03d_%03d.nc" % (
        os.getenv("SCRATCH"),
        max_lat - 1,
        max_lat,
    )
    if not os.path.isfile(opfile):
        mll = max_lat
        if mll == 90:
            mll = 90.1
        print(
            (
                "./make_normalisation_parameters.py --startyear=%04d --endyear=%04d "
                + "--min_lat=%04.1f --max_lat=%04.1f"
            )
            % (
                args.startyear,
                args.endyear,
                max_lat - 1,
                mll,
            )
        )
