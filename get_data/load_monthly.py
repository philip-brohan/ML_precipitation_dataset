# Functions to load monthly data

from get_data import CMORPH
from get_data import Copernicus
from get_data import CRU
from get_data import ERA5
from get_data import GPCC


def load(year=None, month=None, organisation=None, source=None, constraint=None):
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    if organisation is None:
        raise Exception("Organisation must be specified")

    if organisation == "CMORPH":
        if source is None:
            raise Exception("for CMORPH, source must be specified")
        if source == "satellite":
            varC = CMORPH.satellite.CMORPH_s_monthly.load(
                year=year, month=month, constraint=constraint
            )
        else:
            raise Exception("Unsuppported source %s in %s" % (source, organisation))
    elif organisation == "Copernicus":
        if source is None:
            raise Exception("for Copernicus, source must be specified")
        if source == "microwave":
            varC = Copernicus.satellite_microwave.CSM_monthly.load(
                year=year, month=month, variable="precip", constraint=constraint
            )
        elif source == "observations":
            if constraint is not None:
                raise Exception("Can't use constraints with Copernicus obs.")
            varC = Copernicus.land_surface_observations.Cobs_monthly.load(
                year=year,
                month=month,
                category="unrestricted",
            )
        else:
            raise Exception("Unsuppported source %s in %s" % (source, organisation))
    elif organisation == "CRU":
        if source is None:
            raise Exception("for CRU, source must be specified")
        if source == "in-situ":
            varC = CRU.in_situ.CRU_i_monthly.load(
                year=year, month=month, constraint=constraint
            )
        else:
            raise Exception("Unsuppported source %s in %s" % (source, organisation))
    elif organisation == "ERA5":
        varC = ERA5.ERA5_monthly.load(
            year=year,
            month=month,
            variable="total_precipitation",
            constraint=constraint,
        )
    elif organisation == "TWCR":
        varC = TWCR.TWCR_monthly_load.load_monthly_member(
            year=year,
            month=month,
            variable="PRATE",
            constraint=constraint,
        )
    elif organisation == "GPCC":
        if source is None:
            raise Exception("for GPCC, source must be specified")
        if source == "in-situ":
            varC = GPCC.in_situ.GPCC_i_monthly.load(
                year=year, month=month, constraint=constraint
            )
        elif source == "satellite+gauge":
            varC = GPCC.with_satellite.GPCC_s_monthly.load(
                year=year, month=month, variable="precip", constraint=constraint
            )
        else:
            raise Exception("Unsuppported source %s in %s" % (source, organisation))
    else:
        raise Exception("Unsupported organisation %s" % organisation)
    return varC
