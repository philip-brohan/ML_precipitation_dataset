#!/usr/bin/env python

# Make a cube with a mask giving the coverage of the CRU dataset

import os
import iris
from get_data.CRU.in_situ import CRU_i_monthly
from utilities import grids

raw = CRU_i_monthly.load(
    year=1999,
    month=3,
    grid=grids.E5sCube,
)
raw.data.data[raw.data.mask == True] = 0
raw.data.data[raw.data.mask == False] = 1
raw.data = raw.data.data  # Don't bother with masking

lDir = "%s/MLP/visualizations/time_series/masks" % os.getenv("SCRATCH")
if not os.path.exists(lDir):
    os.makedirs(lDir)

iris.save(raw, "%s/CRU.nc" % lDir)
