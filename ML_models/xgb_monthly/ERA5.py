#!/usr/bin/env python

# ERA5 specific functions for the XGBoost model

import os
import sys
import xgboost as xgb

import zarr

import numpy as np

rng = np.random.default_rng()


# Want temperature, precipitation and prate to model
# Get the data from the zarr arrays
def get_zarr(variable):
    fn = "%s/normalized_datasets/ERA5_tf_MM/%s_zarr" % (
        os.getenv("PDIR"),
        variable,
    )
    zarr_array = zarr.open(fn, mode="r")
    return zarr_array


t2m = get_zarr("2m_temperature")
prmsl = get_zarr("mean_sea_level_pressure")
prate = get_zarr("total_precipitation")


# load the selected member, or ensemble mean for a month
def get_month(variable, year, month):
    zf = None
    if variable == "temperature":
        zf = t2m
    elif variable == "pressure":
        zf = prmsl
    elif variable == "precipitation":
        zf = prate
    else:
        raise Exception("Unsupported ERA5 variable %s" % variable)
    d_idx = zf.attrs["AvailableMonths"]["%04d-%02d" % (year, month)]
    mnth = zf[:, :, d_idx]
    return mnth
