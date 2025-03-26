# Functions to load 20CRv3 monthly data

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

from utilities.grids import TWCRCube

warnings.filterwarnings("ignore", message=".*frac.*")

# Only using a subset of the members
members = [
    1,
    2,
    3,
    4,
    5,
    76,
    77,
    78,
    79,
    80,
]


# Need to add coordinate system metadata so they work with iris
coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = coord_s
    cbe.coord("longitude").coord_system = coord_s


# Add a land-mask for TWCR SST grid
lm_TWCR = iris.load_cube(
    "%s/fixed/land.nc" % os.getenv("TWCR_HOURLY")
)  # on 1-degree grid - that's the official version
lm_TWCR = iris.util.squeeze(lm_TWCR)
lm_TWCR.coord("latitude").coord_system = coord_s
lm_TWCR.coord("longitude").coord_system = coord_s
lm_TWCR = lm_TWCR.regrid(TWCRCube, iris.analysis.Linear())
lm_TWCR.data = np.ma.masked_where(lm_TWCR.data > 0.5, lm_TWCR.data, copy=False)
lm_TWCR.data.data[np.where(lm_TWCR.data.mask == True)] = 0
lm_TWCR.data.data[np.where(lm_TWCR.data.mask == False)] = 1


def load_hourly_member(
    variable="PRATE",
    year=None,
    month=None,
    day=None,
    hour=None,
    member=1,
    constraint=None,
):
    if variable == "SST":
        ts = load_hourly_member(
            variable="TMPS",
            year=year,
            month=month,
            day=day,
            hour=hour,
            member=member,
            constraint=constraint,
        )
        ts.data = np.ma.MaskedArray(ts.data, lm_TWCR.data.mask)
        return ts
    else:
        fname = "%s/%04d/%s.%04d_mem%03d.nc" % (
            os.getenv("TWCR_HOURLY"),
            year,
            variable,
            year,
            member,
        )
        if not os.path.isfile(fname):
            raise Exception("No data file %s" % fname)
        ftt = iris.Constraint(
            time=lambda cell: cell.point.month == month
            and cell.point.day == day
            and cell.point.hour == hour
        )
        hslice = iris.load_cube(fname, ftt)
        if variable == "TMP2m":
            hslice = iris.util.squeeze(hslice)
        hslice.coord("latitude").coord_system = coord_s
        hslice.coord("longitude").coord_system = coord_s
        hslice = hslice.regrid(TWCRCube, iris.analysis.Nearest())
        if constraint is not None:
            hslice = hslice.extract(constraint)

        return hslice
