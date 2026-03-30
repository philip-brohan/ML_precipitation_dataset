#!/usr/bin/env python

# Make a climatological mean for one variable and member

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
parser.add_argument(
    "--member",
    type=int,
    required=True,
    help="Ensemble member (1-80)",
)
args = parser.parse_args()

clim = None
for year in range(1961, 1991):
    cube = iris.load_cube(
        "%s/20CR/version_3/hourly/%04d/%s.%04d_mem%03d.nc"
        % (os.getenv("PDIR"), year, args.variable, year, args.member)
    )
    # Get rid of Feb 29th if present
    ftt = iris.Constraint(
        time=lambda cell: not (cell.point.month == 2 and cell.point.day == 29)
    )
    cube = cube.extract(ftt)
    if clim is None:
        clim = cube.copy()
        clim.data *= 0.0
    clim.data += cube.data / 30.0

iris.save(
    clim,
    "%s/20CR/version_3/hourly/climatology_1961-90/%s_mem%03d.nc" % (os.getenv("PDIR"),  args.variable,  args.member),
)
