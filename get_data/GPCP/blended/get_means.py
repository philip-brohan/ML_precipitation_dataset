#!/usr/bin/env python

# Retrieve GPCP monthly means

import os
from urllib.request import urlretrieve


opdir = "%s/GPCP/" % (os.getenv("SCRATCH"))
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)

url = "https://downloads.psl.noaa.gov/Datasets/gpcp/precip.mon.mean.nc"
urlretrieve(url, "%s/precip.mon.mean.nc" % opdir)
