# Functions to load monthly data

import CMORPH
import Copernicus
import CRU
import ERA5
import GPCC


def load(year=None, month=None, organisation=None, source=None):
    if year is None or month is None:
        raise Exception("Year and month must be specified")
    if organisation is None or source is None:
        raise Exception("Organisation and source must be specified")

    if organisation == "CMORPH":
        if source == "satellite":
            varC = CMORPH.satellite.CMORPH_s_monthly.load(year=year, month=month)
        else:
            raise Exception("Unsuppported source %s in %s" % (source, organisation))
    elif organisation == "Copernicus":
        if source == "microwave":
            varC = Copernicus.satellite_microwave.CSM_monthly.load(
                year=year, month=month, variable="precip"
            )
        elif source == "observations":
            varC = Copernicus.land_surface_observations.Cobs_monthly.load(
                year=year, month=month, category="unrestricted"
            )
        else:
            raise Exception("Unsuppported source %s in %s" % (source, organisation))
    elif organisation == "CRU":
        if source == "in-situ":
            varC = CRU.in_situ.CRU_i_monthly.load(year=year, month=month)
        else:
            raise Exception("Unsuppported source %s in %s" % (source, organisation))
    elif organisation == "ERA5":
        varC = ERA5.ERA5_monthly.load(
            year=year, month=month, variable="total_precipitation"
        )
    elif organisation == "GPCC":
        if source == "in-situ":
            varC = GPCC.in_situ.GPCC_i_monthly.load(year=year, month=month)
        elif source == "satellite+gauge":
            varC = GPCC.with_satellite.GPCC_s_monthly.load(
                year=year, month=month, variable="precip"
            )
        else:
            raise Exception("Unsuppported source %s in %s" % (source, organisation))
    else:
        raise Exception("Unsupported organisation %s" % organisation)
    return varC
