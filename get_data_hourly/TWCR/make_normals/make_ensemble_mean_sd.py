#!/usr/bin/env python

# Make an ensemble mean of the member sd for 1961-1990.

import os
import argparse
import iris

parser = argparse.ArgumentParser()
parser.add_argument(
    "--variable",
    type=str,
    default="PRMSL",
    help="TWCR variable name (e.g. PRATE, TMP2m, PRMSL, SST)",
)
args = parser.parse_args()

clim = None
for member in range(1, 81):
    cube = iris.load_cube(
        "%s/20CR/version_3/hourly/sd_1961-90/%s_mem%03d.nc"
        % (os.getenv("PDIR"), args.variable, member)
    )
    if clim is None:
        clim = cube.copy()
        clim.data *= 0.0
    clim.data += cube.data / 80.0

iris.save(
    clim,
    "%s/20CR/version_3/hourly/sd_1961-90/%s_ensmean.nc"
    % (os.getenv("PDIR"), args.variable),
)
