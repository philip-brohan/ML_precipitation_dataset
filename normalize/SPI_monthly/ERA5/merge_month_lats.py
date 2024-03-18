#!/usr/bin/env python

# Merge the normalization parameters across latitude bands and months

import os
import sys
import iris
import iris.cube
import iris.util

# I don't care about datums.
iris.FUTURE.datum_support = True

for param in ("shape", "location", "scale"):
    mmerged = iris.cube.CubeList()
    for month in range(1, 13):
        merged = iris.cube.CubeList()
        for max_lat in range(-89, 91):
            ipfile = "%s/MLP/normalization/SPI_monthly/ERA5/%s_m%02d_%03d_%03d.nc" % (
                os.getenv("SCRATCH"),
                param,
                month,
                max_lat - 1,
                max_lat,
            )
            if not os.path.isfile(ipfile):
                raise Exception("Missing file %s" % ipfile)
            merged.append(iris.load_cube(ipfile))

        junk = iris.util.equalise_attributes(merged)
        merged = merged.concatenate_cube()
        mmerged.append(merged)
    mmerged = mmerged.merge_cube()
    opfile = "%s/MLP/normalization/SPI_monthly/ERA5/%s.nc" % (
        os.getenv("SCRATCH"),
        param,
    )
    iris.save(mmerged, opfile)
