# Functions to load OCADA monthly data

import os
import iris
import iris.util
import iris.cube
import iris.time
import iris.analysis
import iris.coord_systems
import iris.fileformats
import numpy as np
import warnings

warnings.filterwarnings("ignore", message=".*frac.*")

# Need to add coordinate system metadata so they work with iris
coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = coord_s
    cbe.coord("longitude").coord_system = coord_s


def load_monthly(variable="precipi", year=None, month=None, constraint=None, grid=None):
    fname = "%s/OCADA/monthly/means/%s_%04d.nc" % (
        os.getenv("SCRATCH"),
        variable,
        year,
    )
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(time=lambda cell: cell.point.month == month)
    hslice = iris.load_cube(fname, ftt)
    #    if variable == "TMP2m":
    #        hslice = iris.util.squeeze(hslice)
    hslice.coord("latitude").coord_system = coord_s
    hslice.coord("longitude").coord_system = coord_s
    if grid is not None:
        hslice = hslice.regrid(grid, iris.analysis.Linear())
    if constraint is not None:
        hslice = hslice.extract(constraint)

    return hslice


#
