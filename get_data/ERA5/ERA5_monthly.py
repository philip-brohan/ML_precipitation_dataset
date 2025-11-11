# Functions to load ERA5 monthly data

import os
import iris
import iris.util
import iris.coord_systems
import numpy as np

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True

# ERA5 data does not have explicit coordinate systems
# Specify one to add on load so the cubes work properly with iris.
cs_ERA5 = iris.coord_systems.RotatedGeogCS(90, 180, 0)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = cs_ERA5
    cbe.coord("longitude").coord_system = cs_ERA5


def load(
    variable="total_precipitation", year=None, month=None, constraint=None, grid=None
):
    if variable == "land_mask":
        varC = load("sea_surface_temperature", year=2020, month=3, grid=grid)
        varC.data.data[np.where(varC.data.mask == True)] = 0
        varC.data.data[np.where(varC.data.mask == False)] = 1
        return varC
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    fname = "%s/ERA5/monthly/reanalysis/%04d/%s.nc" % (
        os.getenv("PDIR"),
        year,
        variable,
    )
    long_names = {
        "total_precipitation": "Total precipitation",
        "2m_temperature": "2 metre temperature",
        "sea_surface_temperature": "Sea surface temperature",
        "mean_sea_level_pressure": "Mean sea level pressure",
    }
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(time=lambda cell: cell.point.month == month)
    varC = iris.load_cube(fname, long_names[variable])
    varC.remove_coord("expver")  # Weird ERA5 feature breaks iris
    varC = varC.extract(ftt)  # Must remove expver before applying constraint
    add_coord_system(varC)
    varC.long_name = variable
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Nearest())
    if constraint is not None:
        varC = varC.extract(constraint)
    return varC


def load_climatology(variable, month, constraint=None):
    fname = "%s/ERA5/monthly/climatology/%s_%02d.nc" % (
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
    add_coord_system(c)
    c.long_name = variable
    return c


def load_sd_climatology(variable, month, constraint=None):
    fname = "%s/ERA5/monthly/sd_climatology/%s_%02d.nc" % (
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
    add_coord_system(c)
    c.long_name = variable
    return c
