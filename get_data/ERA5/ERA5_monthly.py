# Functions to load ERA5 monthly data

import os
import iris
import iris.util
import iris.coord_systems
import numpy as np

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True

# ERA5 data does not have explicit coodinate systems
# Specify one to add on load so the cubes work properly with iris.
cs_ERA5 = iris.coord_systems.RotatedGeogCS(90, 180, 0)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = cs_ERA5
    cbe.coord("longitude").coord_system = cs_ERA5


def load(variable="total_precipitation", year=None, month=None):
    if variable == "land_mask":
        varC = load("sea_surface_temperature", year=2020, month=3)
        lm_ERA5.data.data[np.where(lm_ERA5.data.mask == True)] = 0
        lm_ERA5.data.data[np.where(lm_ERA5.data.mask == False)] = 1
        add_coord_system(varC)
        return varC
    if year is None or month is None:
        raise Exception('Year and month must be specified')
    fname = "%s/ERA5/monthly/reanalysis/%04d/%s.nc" % (
        os.getenv("SCRATCH"),
        year,
        variable,
    )
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(time=lambda cell: cell.point.month == month)
    varC = iris.load_cube(fname, ftt)
    # Get rid of unnecessary height dimensions
    if len(varC.data.shape) == 3:
        varC = varC.extract(iris.Constraint(expver=1))
    add_coord_system(varC)
    varC.long_name = variable
    return varC


def load_climatology(variable, month):
    fname = "%s/ERA5/monthly/climatology/%s_%02d.nc" % (
        os.getenv("SCRATCH"),
        variable,
        month,
    )
    if not os.path.isfile(fname):
        raise Exception("No climatology file %s" % fname)
    c = iris.load_cube(fname)
    add_coord_system(c)
    c.long_name = variable
    return c


def load_sd_climatology(variable, month):
    fname = "%s/ERA5/monthly/sd_climatology/%s_%02d.nc" % (
        os.getenv("SCRATCH"),
        variable,
        month,
    )
    if not os.path.isfile(fname):
        raise Exception("No sd climatology file %s" % fname)
    c = iris.load_cube(fname)
    add_coord_system(c)
    c.long_name = variable
    return c
