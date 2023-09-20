#!/usr/bin/env python

# Merge the normalisation parameters across latitude bands and months

import os
import sys
import iris
import iris.cube
import iris.util
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--variable", type=str, required=False, default="PRATE")
args = parser.parse_args()

# I don't care about datums.
iris.FUTURE.datum_support = True

for param in ("shape", "location", "scale"):
    mmerged = iris.cube.CubeList()
    for month in range(1, 13):
        merged = iris.cube.CubeList()
        for max_lat in range(-89, 91, 1):
            ipfile = (
                "%s/MLP/normalisation/SPI_monthly/TWCR/%s/%s_m%02d_%03d_%03d.nc"
                % (
                    os.getenv("SCRATCH"),
                    args.variable,
                    param,
                    month,
                    max_lat - 1,
                    max_lat,
                )
            )
            if not os.path.isfile(ipfile):
                raise Exception("Missing file %s" % ipfile)
            merged.append(iris.load_cube(ipfile))

        junk = iris.util.equalise_attributes(merged)
        merged = merged.concatenate_cube()
        mmerged.append(merged)
    junk = iris.util.equalise_attributes(mmerged)
    mmerged = mmerged.merge_cube()
    opfile = "%s/MLP/normalisation/SPI_monthly/TWCR/%s/%s.nc" % (
        os.getenv("SCRATCH"),
        args.variable,
        param,
    )
    iris.save(mmerged, opfile)
