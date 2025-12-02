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
import xgboost as xgb
import pickle
from utils import get_source_and_target, to_DMatrix

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Test year", type=int, required=False, default=1969)
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
else:
    print("Target %s not recognised" % args.target)
    sys.exit(1)


# Get the predictions for a month
def get_predictions(model, source, target, feature_names=None):
    dm = to_DMatrix(source, target, feature_names=feature_names)
    preds = model.predict(dm)
    return preds


# Reduce a field to a scalar (mean or otherwise)
def reduce_to_scalar(field):
    return np.mean(field)


# Make timeseries by doing data retrieval, modelling, and reduction for each month
date_ts = []
prediction_ts = []
target_ts = []
feature_names = None
for year in range(args.start_year, args.end_year + 1):
    for month in range(1, 13):
        source, target, feature_names = get_source_and_target(
            get_s_month,
            get_t_month,
            year,
            year,
            start_month=month,
            end_month=month,
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
        date_ts.append("%04d-%02d" % (year, month))
        prediction_ts.append(reduce_to_scalar(prediction))
        target_ts.append(reduce_to_scalar(target))

# save the time-series results
opdir = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/ts_validation/"
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
