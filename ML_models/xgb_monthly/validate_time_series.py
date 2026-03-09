#!/usr/bin/env python

# Get data for a validation time-series
# Gets data for a single year - run many times (in parallel) to get data for a period

# Show:
#  1) Target field
#  2) Model output
#  3) scatter plot

import os
import sys
import numpy as np
import zarr
import xgboost as xgb
from utils import get_source_and_target, to_DMatrix

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
import tensorstore as ts

import dask

# Going to do external parallelism - run this on one core
tf.config.threading.set_inter_op_parallelism_threads(1)
dask.config.set(scheduler="single-threaded")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Test year", type=int, required=True)
parser.add_argument(
    "--member_idx", help="Member index (0-9)", type=int, required=False, default=None
)
parser.add_argument(
    "--mlabel",
    type=str,
    required=True,
)
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--no_uwind", action="store_true")
parser.add_argument("--no_vwind", action="store_true")
parser.add_argument("--no_humidity", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
parser.add_argument("--lat_offset", type=int, required=False, default=None)
parser.add_argument("--lon_offset", type=int, required=False, default=None)
parser.add_argument(
    "--month",
    type=int,
    required=True,
    default=2023,
)
parser.add_argument(
    "--label",  # name for this validation run
    type=str,
    required=True,
    default=None,
)
parser.add_argument(
    "--source",
    type=str,  # 'TWCR','ERA5', or 'GC5'
    required=True,
    default=None,
)
parser.add_argument(
    "--target",
    type=str,  # 'TWCR','ERA5','GC5','GPCC','CRU','GPCP'
    required=True,
    default=None,
)
args = parser.parse_args()
if args.target is None:
    args.target = args.source

ipdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")
# Load the model
fname = "%s/%s.ubj" % (ipdir, args.mlabel)
model = xgb.Booster()
model.load_model(fname)

if args.source == "TWCR":
    from TWCR import get_month as get_s_month
elif args.source == "ERA5":
    from ERA5 import get_month as get_s_month
elif args.source == "GC5":
    from GC5 import get_month as get_s_month
else:
    print("Source %s not recognised" % args.source)
    sys.exit(1)
if args.target == "TWCR":
    from TWCR import get_month as get_t_month
elif args.target == "ERA5":
    from ERA5 import get_month as get_t_month
elif args.target == "GC5":
    from GC5 import get_month as get_t_month
elif args.target == "CRU":
    from CRU import get_month as get_t_month
else:
    print("Target %s not recognised" % args.target)
    sys.exit(1)


# Get the predictions for a month
def get_predictions(model, source, target, feature_names=None):
    valid_rows = np.isfinite(source).all(axis=1) & np.isfinite(target)
    s2 = source[valid_rows]
    t2 = target[valid_rows]
    dm = to_DMatrix(s2, t2, feature_names=feature_names)
    preds = model.predict(dm)
    preds_full = np.full(target.shape, np.nan)
    preds_full[valid_rows] = preds
    return preds_full


# Make field by doing data retrieval and modelling for each month
date_ts = []
prediction_ts = []
target_ts = []
feature_names = None
source, target, feature_names = get_source_and_target(
    get_s_month,
    get_t_month,
    args.year,
    args.year,
    start_month=args.month,
    end_month=args.month,
    no_temperature=args.no_temperature,
    no_pressure=args.no_pressure,
    no_uwind=args.no_uwind,
    no_vwind=args.no_vwind,
    no_humidity=args.no_humidity,
    fix_lat=args.fix_lat,
    fix_lon=args.fix_lon,
    fix_month=args.fix_month,
    lat_offset=args.lat_offset,
    lon_offset=args.lon_offset,
)
prediction = get_predictions(model, source, target, feature_names=feature_names)

# save the model field
opdir = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/ts_validation"

fn = "%s/model_zarr" % (opdir,)

dataset = ts.open(
    {
        "driver": "zarr",
        "kvstore": "file://" + fn,
    }
).result()
zarr_ds = zarr.open(fn, mode="r+")
FirstYear = zarr_ds.attrs["FirstYear"]
idx = (args.year - FirstYear) * 12 + (args.month - 1)
op = dataset[:, :, idx].write(prediction.reshape([721, 1440]).astype(np.float32))
op.result()  # Ensure write completes before exiting
