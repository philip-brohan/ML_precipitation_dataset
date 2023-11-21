# Functions to load GPCC satellite+gauge monthly data

import os
import iris
import iris.coord_systems

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True

# GPCC data does not have explicit coodinate systems
# Specify one to add on load so the cubes work properly with iris.
GPCC_CMS = iris.coord_systems.RotatedGeogCS(90, 180, 0)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = GPCC_CMS
    cbe.coord("longitude").coord_system = GPCC_CMS


def load(year=None, month=None, grid=None):
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    fname = (
        "%s/GPCC/satellite+gauge/monthly/precipitation/%04d/"
        + "gpcp_v02r03_monthly_d%04d%02d.nc"
    ) % (
        os.getenv("SCRATCH"),
        year,
        year,
        month,
    )
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    varC = iris.load_cube(fname,iris.NameConstraint(var_name="precip"))
    varC = iris.util.squeeze(varC)
    add_coord_system(varC)
    varC.data.data[varC.data.mask] = -1
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Nearest())
    return varC
