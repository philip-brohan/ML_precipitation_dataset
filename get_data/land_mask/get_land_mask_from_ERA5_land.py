#!/usr/bin/env python

# Retrieve a soil temperature file from ERA5-land

# This is just an easy way to get a high-resolution land mask for plotting

import os
import cdsapi

opdir = "%s/ERA5/monthly/reanalysis" % os.getenv("PDIR")
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)

if not os.path.isfile("%s/land_mask.nc" % opdir):  # Only bother if we don't have it

    c = cdsapi.Client()

    # Variable and date are arbitrary
    # Just want something that is only defined in land grid-cells.

    ctrlB = {
        "variable": ["land_sea_mask"],
        "data_format": "netcdf",
        "download_format": "unarchived"
    }


    c = cdsapi.Client()
    c.retrieve(
        "reanalysis-era5-land-monthly-means",
        ctrlB,
        "%s/%s.nc" % (opdir, "land_mask"),
    )
