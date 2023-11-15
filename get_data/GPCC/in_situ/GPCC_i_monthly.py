# Functions to load GPCC in-situ monthly data

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
        "%s/GPCC/in-situ/monthly/precipitation/%04d/"
        + "GPCC_total_precipitation_mon_0.25x0.25_global_%04d_v2020.0.nc"
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
    # Without this regriding sometimes gives nonsense - why?
    varC.data.data[varC.data.mask] = -1
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Nearest())
    return varC
