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

warnings.filterwarnings("ignore", message=".*frac.*")

# Need to add coordinate system metadata so they work with iris
coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = coord_s
    cbe.coord("longitude").coord_system = coord_s

# Add a land-mask for TWCR SST grid
lm_TWCR = iris.load_cube("%s/20CR/version_3/fixed/land.nc" % os.getenv("SCRATCH"))
lm_TWCR = iris.util.squeeze(lm_TWCR)
lm_TWCR.coord("latitude").coord_system = coord_s
lm_TWCR.coord("longitude").coord_system = coord_s
lm_TWCR.data = np.ma.masked_where(lm_TWCR.data > 0.0, lm_TWCR.data, copy=False)
lm_TWCR.data.data[np.where(lm_TWCR.data.mask == True)] = 0
lm_TWCR.data.data[np.where(lm_TWCR.data.mask == False)] = 1


def load_monthly_member(
    variable="PRATE", year=None, month=None, member=1, constraint=None, grid=None
):
    if variable == "SST":
        ts = load_monthly_member(
            variable="TMPS",
            year=year,
            month=month,
            member=member,
            constraint=constraint,
        )
        return ts
    else:
        fname = "%s/20CR/version_3/monthly/members/%04d/%s.%04d.mnmean_mem%03d.nc" % (
            os.getenv("SCRATCH"),
            year,
            variable,
            year,
            member,
        )
        if not os.path.isfile(fname):
            raise Exception("No data file %s" % fname)
        ftt = iris.Constraint(time=lambda cell: cell.point.month == month)
        hslice = iris.load_cube(fname, ftt)
        if variable == "TMP2m":
            hslice = iris.util.squeeze(hslice)
        hslice.coord("latitude").coord_system = coord_s
        hslice.coord("longitude").coord_system = coord_s
        if grid is not None:
            hslice = hslice.regrid(grid,iris.analysis.Linear())
        if constraint is not None:
            hslice = hslice.extract(constraint)

        return hslice


def load_monthly_ensemble(variable='PRATE', year=None, month=None,constraint=None,grid=None):
    fname = "%s/20CR/version_3/monthly/members/%04d/%s.%04d.mnmean_mem*.nc" % (
        os.getenv("SCRATCH"),
        year,
        variable,
        year,
    )
    ftt = iris.Constraint(time=lambda cell: cell.point.month == month)
    hslice = iris.load(fname, ftt)
    for i, cb in enumerate(hslice):
        cb.coord("latitude").coord_system = coord_s
        cb.coord("longitude").coord_system = coord_s
        if grid is not None:
            cb = cb.regrid(grid,iris.analysis.Linear())
        if constraint is not None:
            cb = cb.extract(constraint)
        cb.add_aux_coord(
            iris.coords.AuxCoord(
                cb.attributes["realization"], standard_name="realization"
            )
        )
        del cb.attributes["realization"]
        del cb.attributes["history"]
        cb = iris.util.new_axis(cb, "realization")
        hslice[i] = cb
    hslice = hslice.concatenate_cube()


    return hslice

