#!/usr/bin/env python

# Plot a validation figure for the xgb model
# Time-series, do the validation for a series of months and calculate a mean for each

# Show:
#  1) Target field
#  2) Model output
#  3) scatter plot

import os
import numpy as np
import xgboost as xgb
import zarr
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Test year", type=int, required=False, default=1969)
parser.add_argument("--month", help="Test month", type=int, required=False, default=3)
parser.add_argument(
    "--member_idx", help="Member index (0-9)", type=int, required=False, default=None
)
parser.add_argument(
    "--mlabel",
    type=str,
    required=False,
    default=None,
)
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
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
    "--label",  # name for this validation run
    type=str,
    required=True,
    default=None,
)
args = parser.parse_args()

ipdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")
# Load the model
if args.mlabel is None:
    fname = "%s/TWCR.ubj" % ipdir
else:
    fname = "%s/TWCR_%s.ubj" % (ipdir, args.mlabel)
model = xgb.Booster()
model.load_model(fname)

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

# Get Fields for month
def get_data_for_month(year,month):
    m_temperature = get_month(t2m, year, month).flatten()
    if args.no_temperature:
        m_temperature = np.full_like(m_temperature, 0.5)
    m_pressure = get_month(prmsl, year, month).flatten()
    if args.no_pressure:
        m_pressure = np.full_like(m_pressure, 0.5)
    m_precip = get_month(prate, year, month).flatten()
    m_latitude = lat_idx.flatten() / 720
    if args.fix_lat is not None:
        m_latitude = np.full_like(m_latitude, args.fix_lat / 180 + 0.5)
    m_longitude = lon_idx.flatten() / 1440
    if args.fix_lon is not None:
        m_longitude = np.full_like(m_longitude, args.fix_lon / 360 + 0.5)
    m_month = np.full_like(m_temperature, month)
    if args.fix_month is not None:
        m_month = np.full_like(m_month, args.fix_month)
    # Combine into feature array
    source = np.column_stack(
        (m_pressure, m_temperature, m_latitude, m_longitude, m_month)
    )
    # Get this month's target similarly
    target = m_precip
    return source,target

# Get the predictions for a month
def get_predictions(model,source):
    source = xgb.DMatrix(data=source)
    preds = model.predict(source)
    return preds

# Reduce a field to a scalar (mean or otherwise)
def reduce_to_scalar(field):
    return np.mean(field)

# Make timestires by doing data retrieval, modelling, and reduction for each month
date_ts = []
prediction_ts = []
target_ts=[]
for year in range(args.start_year,args.end_year+1):
    for month in range(1,13):
       print("%04d-%02d" % (year,month))
       source,target = get_data_for_month(year,month)
       prediction = get_predictions(model,source)
       date_ts.append("%04d-%02d" % (year,month))
       prediction_ts.append(reduce_to_scalar(prediction))
       target_ts.append(reduce_to_scalar(target))

# save the time-series results
opdir = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/ts_validation/{args.label}/"
if not os.path.isdir(opdir):
    os.makedirs(opdir)
out_name = f"{args.start_year:04d}_{args.end_year:04d}.pkl"
out_path = os.path.join(opdir, out_name)
with open(out_path, "wb") as of:
    pickle.dump(
        {
            "date_ts": date_ts,
            "prediction_ts": prediction_ts,
            "target_ts": target_ts,
            "args": vars(args),
        },
        of,
        protocol=pickle.HIGHEST_PROTOCOL,
    )
print("Saved time-series pickle to", out_path)