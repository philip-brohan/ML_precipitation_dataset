# Functions to load HadISST

import os
import iris
import iris.coord_systems

# Specify a coordinate system to add on load so the cubes work properly with iris.
CMS = iris.coord_systems.RotatedGeogCS(90, 180, 0)

version = "v1"
opdir = "%s/HadISST/%s" % (os.getenv("SCRATCH"), version)


# Add a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = CMS
    cbe.coord("longitude").coord_system = CMS


def load(year=None, month=None, grid=None):
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    fname = "%s/HadISST_sst.nc" % opdir
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(
        time=lambda cell: cell.point.month == month and cell.point.year == year
    )
    varC = iris.load_cube(fname, "sea_surface_temperature" & ftt)
    add_coord_system(varC)
    # Set sea-ice-covered SST to missing
    varC.data.mask[varC.data.data < -1] = True
    # Without this regriding sometimes gives nonsense - why?
    varC.data.data[varC.data.mask] = -1
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Linear())

    return varC
