#!/usr/bin/env python

# Merge the normalization parameters across latitude bands

import os
import iris
import iris.cube
import iris.util

# I don't care about datums.
iris.FUTURE.datum_support = True

for param in ("shape", "location", "scale"):
    merged = iris.cube.CubeList()
    for max_lat in range(-89, 91):
        ipfile = "%s/MLP/normalization/SPI/ERA5/%s_%03d_%03d.nc" % (
            os.getenv("SCRATCH"),
            param,
            max_lat - 1,
            max_lat,
        )
        if not os.path.isfile(ipfile):
            raise Exception("Missing file %s" % ipfile)
        merged.append(iris.load_cube(ipfile))

    junk = iris.util.equalise_attributes(merged)
    merged = merged.concatenate_cube()
    opfile = "%s/MLP/normalization/SPI/ERA5/%s.nc" % (
        os.getenv("SCRATCH"),
        param,
    )
    iris.save(merged, opfile)
