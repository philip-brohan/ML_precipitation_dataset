#!/usr/bin/env python

# Make a cube with a mask giving the coverage of Europe (well observed area)

import os
import sys
import numpy as np
import iris
from get_data.CRU.in_situ import CRU_i_monthly
from utilities import grids

raw = grids.E5sCube.copy()
lats = raw.coord("grid_latitude").points
lons = raw.coord("grid_longitude").points
lons, lats = np.meshgrid(lons, lats)
raw.data *= 0
raw.data += 1
raw.data[(lons < -15) | (lons > 30)] = 0
raw.data[(lats < 35) | (lats > 65)] = 0

lDir = "%s/MLP/visualizations/time_series/masks" % os.getenv("SCRATCH")
if not os.path.exists(lDir):
    os.makedirs(lDir)

iris.save(raw, "%s/Europe.nc" % lDir)
