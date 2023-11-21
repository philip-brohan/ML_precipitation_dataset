# Functions to load CRU in-situ monthly data

import os
import iris
import iris.coord_systems

# Data does not have explicit coodinate systems
# Specify one to add on load so the cubes work properly with iris.
CMS = iris.coord_systems.RotatedGeogCS(90, 180, 0)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = CMS
    cbe.coord("longitude").coord_system = CMS


def load(year=None, month=None, grid=None):
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    fname = ("%s/GPCP/precip.mon.mean.nc") % (os.getenv("SCRATCH"),)
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(
        time=lambda cell: cell.point.year == year and cell.point.month == month
    )
    fn = iris.NameConstraint(var_name="precip")
    varC = iris.load_cube(fname, fn & ftt)
    add_coord_system(varC)
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Linear())
    return varC
