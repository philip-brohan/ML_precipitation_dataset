# Functions to load CMORPH satellite monthly data

import os
import iris
import iris.coord_systems
import numpy as np

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True

# CMORPH data does not have explicit coodinate systems
# Specify one to add on load so the cubes work properly with iris.
cs_CMS = iris.coord_systems.RotatedGeogCS(90, 180, 0)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = cs_CMS
    cbe.coord("longitude").coord_system = cs_CMS


def load(year=None, month=None):
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    fname = (
        "%s/CMORPH/satellite+/monthly/precipitation/%04d/"
        + "CMORPH_total_precipitation_mon_0.5x0.5_quasi-global_%04d_v1.0.nc"
    ) % (
        os.getenv("SCRATCH"),
        year,
        year,
    )
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(time=lambda cell: cell.point.month == month)
    varC = iris.load_cube(fname, ftt)
    add_coord_system(varC)
    return varC
