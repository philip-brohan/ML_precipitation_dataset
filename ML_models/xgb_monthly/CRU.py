#!/usr/bin/env python

# CRU specific functions for the XGBoost model

import os
import sys
import xgboost as xgb

import zarr

import numpy as np

rng = np.random.default_rng()


# Want temperature, precipitation and prate to model
# Get the data from the zarr arrays
def get_zarr(variable):
    fn = "%s/normalized_datasets/CRU_tf_MM/%s_zarr" % (
        os.getenv("PDIR"),
        variable,
    )
    zarr_array = zarr.open(fn, mode="r")
    return zarr_array


prate = get_zarr("precipitation")


# load the selected member, or ensemble mean for a month
def get_month(variable, year, month):
    zf = None
    if variable != "precipitation":
        raise Exception("Unsupported CRU variable %s" % variable)
    zf = prate
    try:
        d_idx = zf.attrs["AvailableMonths"]["%04d-%02d" % (year, month)]
        mnth = zf[:, :, d_idx]
        # Set values of 0 to np.nan
        mnth[mnth == 0] = np.nan
    except KeyError:
        mnth = np.full((721, 1440), np.nan)
    return mnth
