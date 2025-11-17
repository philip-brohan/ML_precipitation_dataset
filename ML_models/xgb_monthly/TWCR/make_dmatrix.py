#!/usr/bin/env python

# Turn samples from the normalized tensors into a DMatrix ready for XGBoost

import os
import sys
import xgboost as xgb

import zarr

import numpy as np

rng = np.random.default_rng()

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--start_year",
    type=int,
    required=False,
    default=1850,
)
parser.add_argument(
    "--end_year",
    type=int,
    required=False,
    default=2023,
)
parser.add_argument(
    "--samples",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--member_idx",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--label",
    type=str,
    required=False,
    default=None,
)
args = parser.parse_args()


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
prate = get_zarr("PRATE")


# load the selected member, or ensemble mean for a month
def get_month(zf, year, month):
    d_idx = zf.attrs["AvailableMonths"]["%04d-%02d_00" % (year, month)]
    mnth = zf[:, :, :, d_idx]
    if args.member_idx is not None:
        mnth = mnth[:, :, args.member_idx]
    else:
        mnth = mnth.mean(axis=2)
    return mnth


# lat and long indices are the same for all fields
lat_idx = np.transpose(np.tile(np.arange(721, dtype=int), (1440, 1)))
lon_idx = np.tile(np.arange(1440, dtype=int), (721, 1))

# Source is a n*5 array containing 5 features:
#  pressure, temperature, latitude, longitude, month (all normalised)
# Target is an n*1 array containing one feature:
#  precipitation (normalised)
# we add args.sample rows to each array from each month
source = None
target = None

for year in range(args.start_year, args.end_year + 1):
    for month in range(1, 13):
        m_temperature = get_month(t2m, year, month).flatten()
        m_pressure = get_month(prmsl, year, month).flatten()
        m_precip = get_month(prate, year, month).flatten()
        m_latitude = lat_idx.flatten() / 720
        m_longitude = lon_idx.flatten() / 1440
        m_month = month + m_temperature * 0
        # Subsample?
        if args.samples is not None:
            # pick `args.samples` indices (without replacement) from this month's grid
            npoints = m_temperature.size
            if args.samples >= npoints:
                # nothing to do, requested more/equal points than available
                sel = np.arange(npoints, dtype=int)
            else:
                sel = rng.choice(npoints, size=args.samples, replace=False)
            # apply the same selection to all arrays so they stay aligned
            m_temperature = m_temperature[sel]
            m_pressure = m_pressure[sel]
            m_precip = m_precip[sel]
            m_latitude = m_latitude[sel]
            m_longitude = m_longitude[sel]
            m_month = m_month[sel]
        # Combine into feature array
        m_source = np.column_stack(
            (m_pressure, m_temperature, m_latitude, m_longitude, m_month)
        )
        # Get this month's target similarly
        m_target = m_precip
        # Concatenate the monthly source and target onto the accumulator arrays
        if source is None:
            source = m_source
            target = m_target
        else:
            source = np.concatenate((source, m_source), axis=0)
            target = np.concatenate((target, m_target), axis=0)

# Save the files as xgboost DMatrix native
opdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")
if not os.path.isdir(opdir):
    os.makedirs(opdir)
if args.label is None:
    fname = "%s/TWCR.dt" % opdir
else:
    fname = "%s/TWCR_%s.dt" % (opdir, args.label)

# print(
#     "source.shape, source.dtype:",
#     getattr(source, "shape", None),
#     getattr(source, "dtype", None),
# )
# print(
#     "target.shape, target.dtype:",
#     getattr(target, "shape", None),
#     getattr(target, "dtype", None),
# )
# print("source sample (first 3 rows):\n", source[:3])
# print("target sample (first 10):\n", target[:10])
# print(
#     "target stats: min, mean, max:",
#     float(np.nanmin(target)),
#     float(np.nanmean(target)),
#     float(np.nanmax(target)),
# )


# small_check = xgb.DMatrix(data=source[:10, :], label=target[:10])
# print("small_check rows,cols:", small_check.num_row(), small_check.num_col())
# print("small_check labels:", small_check.get_label())

dtrain = xgb.DMatrix(data=source, label=target)
dtrain.save_binary(fname)
