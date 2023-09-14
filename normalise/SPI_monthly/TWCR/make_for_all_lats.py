#!/usr/bin/env python

# Normalise the TWCR data for all latitude bands

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=1850)
parser.add_argument("--endyear", type=int, required=False, default=2014)
parser.add_argument("--variable", type=str, required=False, default="PRATE")
args = parser.parse_args()

for month in range(1, 13):
    for max_lat in range(-85, 95, 5):
        opfile = "%s/MLP/normalisation/SPI_monthly/TWCR/%s/shape_m%02d_%03d_%03d.nc" % (
            os.getenv("SCRATCH"),
            args.variable,
            month,
            max_lat - 5,
            max_lat,
        )
        if not os.path.isfile(opfile):
            mll = max_lat
            if mll == 90:
                mll = 90.1
            print(
                (
                    "./make_normalisation_parameters.py --startyear=%04d --endyear=%04d "
                    + "--min_lat=%04.1f --max_lat=%04.1f --month=%d --variable=%s"
                )
                % (
                    args.startyear,
                    args.endyear,
                    max_lat - 5,
                    mll,
                    month,
                    args.variable,
                )
            )
