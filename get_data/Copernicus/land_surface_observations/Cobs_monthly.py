# Functions to load Copernicus land surface observations monthly data

import os
import glob
import pandas

def load(year=None, month=None, category='unrestricted'):
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    fname = glob.glob(
        "%s/Copernicus/land_surface_observations/monthly/precipitation/%s/%04d/*%04d-%02d*.csv"
        % (
            os.getenv("SCRATCH"),
            category,
            year,
            year,
            month,
        )
    )
    if len(fname)==0:
        raise Exception("No observations data file found")
    fname=fname[0]
    varC = pandas.read_csv(fname)
    return varC