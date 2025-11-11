# Functions to load GC5-Central monthly data

import os
import iris
import numpy as np

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True


def load(
    variable="prate", run="dl339", year=None, month=None, constraint=None, grid=None
):
    if variable == "land_mask":
        varC = load("sea_surface_temperature", year=2020, month=3, grid=grid)
        varC.data.data[np.where(varC.data.mask == True)] = 0
        varC.data.data[np.where(varC.data.mask == False)] = 1
        return varC
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    if variable == "t2m":
        fname = "%s/GC5-Central/Historical/monthly/%s/%04d.pp" % (
            os.getenv("PDIR"),
            run,
            year,
        )
    else:
        fname = "%s/GC5-Central/Historical/monthly/%s/%s_%04d.pp" % (
            os.getenv("PDIR"),
            run,
            variable,
            year,
        )

    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(time=lambda cell: cell.point.month == month)
    varC = iris.load(fname, ftt)[0]
    # Get rid of unnecessary height dimensions
    if len(varC.data.shape) == 3:
        varC = varC.extract(iris.Constraint(expver=1))
    varC.long_name = variable
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Nearest())
    if constraint is not None:
        varC = varC.extract(constraint)
    # Convert to masked array (for consistency with other data sources).
    varC.data = np.ma.MaskedArray(varC.data, mask=np.zeros(varC.data.shape, dtype=bool))
    return varC


def load_climatology(variable, month, constraint=None):
    fname = "%s/GC5-Central/monthly/climatology/%s_%02d.nc" % (
        os.getenv("PDIR"),
        variable,
        month,
    )
    if not os.path.isfile(fname):
        raise Exception("No climatology file %s" % fname)
    if constraint is not None:
        c = iris.load_cube(fname, constraint)
    else:
        c = iris.load_cube(fname)
    c.long_name = variable
    return c


def load_sd_climatology(variable, month, constraint=None):
    fname = "%s/GC5-Central/monthly/sd_climatology/%s_%02d.nc" % (
        os.getenv("PDIR"),
        variable,
        month,
    )
    if not os.path.isfile(fname):
        raise Exception("No sd climatology file %s" % fname)
    if constraint is not None:
        c = iris.load_cube(fname, constraint)
    else:
        c = iris.load_cube(fname)
    c.long_name = variable
    return c
