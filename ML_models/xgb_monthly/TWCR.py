#!/usr/bin/env python

# TWCR specific functions for the XGBoost model

import os
import sys
import xgboost as xgb

import zarr

import numpy as np

rng = np.random.default_rng()


# Want temperature, precipitation and prate to model
# Get the data from the zarr arrays
def get_zarr(variable):
    fn = "%s/normalized_datasets/TWCR_tf_MM/%s_zarr" % (
        os.getenv("PDIR"),
        variable,
    )
    zarr_array = zarr.open(fn, mode="r")
    return zarr_array


t2m = get_zarr("TMP2m")
prmsl = get_zarr("PRMSL")
prmsl_sd = get_zarr("PRMSL_sd")
prate = get_zarr("PRATE")
uwnd = get_zarr("UGRD10m")
vwnd = get_zarr("VGRD10m")
rh = get_zarr("RH2m")


# load the selected member, or ensemble mean for a month
def get_month(variable, year, month, member_idx=None):
    zf = None
    if variable == "temperature":
        zf = t2m
    elif variable == "pressure":
        zf = prmsl
    elif variable == "pressure_sd":
        zf = prmsl_sd
    elif variable == "precipitation":
        zf = prate
    elif variable == "uwind":
        zf = uwnd
    elif variable == "vwind":
        zf = vwnd
    elif variable == "humidity":
        zf = rh
    else:
        raise Exception("Unsupported TWCR variable %s" % variable)
    try:
        d_idx = zf.attrs["AvailableMonths"]["%04d-%02d_00" % (year, month)]
        mnth = zf[:, :, :, d_idx]
        if member_idx is not None:
            mnth = mnth[:, :, member_idx]
        else:
            mnth = mnth.mean(axis=2)
    except KeyError:
        mnth = np.full((721, 1440), np.nan)
    return mnth
