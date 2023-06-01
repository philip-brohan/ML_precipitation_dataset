# Functions to load Copernicus microwave satellite monthly data

import os
import iris
import iris.util
import iris.coord_systems

# Don't really understand this, but it gets rid of the error messages.
iris.FUTURE.datum_support = True

# This data does not have explicit coodinate systems
# Specify one to add on load so the cubes work properly with iris.
CMS = iris.coord_systems.RotatedGeogCS(90, 180, 0)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = CMS
    cbe.coord("longitude").coord_system = CMS


# As well as 'precip', have precip_stdv, num_obs, num_covered_hours, and quality_flag
def load(year=None, month=None, variable='precip'):
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    fname = (
        "%s/Copernicus/satellite_microwave/monthly/precipitation/%04d/"
        + "COBRA_%04d-%02d_1DM_v1.0.nc"
    ) % (
        os.getenv("SCRATCH"),
        year,
        year,
        month,
    )
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    varC = iris.load_cube(fname, variable)
    # Get rid of unnecessary time dimensions
    varC = iris.util.squeeze(varC)
    add_coord_system(varC)
    return varC