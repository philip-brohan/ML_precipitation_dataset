#!/usr/bin/env python

# Turn samples from the normalized tensors into a DMatrix ready for XGBoost

import os
import sys
import numpy as np

rng = np.random.default_rng()
from utils import get_source_and_target, to_DMatrix
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
parser.add_argument(
    "--opdir",
    type=str,
    required=False,
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
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_pressure_sd", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--no_uwind", action="store_true")
parser.add_argument("--no_vwind", action="store_true")
parser.add_argument("--no_humidity", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
parser.add_argument("--lat_offset", type=int, required=False, default=None)
parser.add_argument("--lon_offset", type=int, required=False, default=None)

args = parser.parse_args()
if args.target is None:
    args.target = args.source

# Load the data entry function - source specific
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


source, target, feature_names = get_source_and_target(
    get_s_month,
    get_t_month,
    args.start_year,
    args.end_year,
    samples=args.samples,
    no_temperature=args.no_temperature,
    no_pressure=args.no_pressure,
    no_pressure_sd=args.no_pressure_sd,
    no_uwind=args.no_uwind,
    no_vwind=args.no_vwind,
    no_humidity=args.no_humidity,
    fix_lat=args.fix_lat,
    fix_lon=args.fix_lon,
    fix_month=args.fix_month,
    lat_offset=args.lat_offset,
    lon_offset=args.lon_offset,
)

# Filter out any rows where any component of source or target is NaN
valid_rows = np.isfinite(source).all(axis=1) & np.isfinite(target)
source = source[valid_rows]
target = target[valid_rows]

dm = to_DMatrix(source, target, feature_names=feature_names)

# Save the files as xgboost DMatrix native
if args.opdir is None:
    args.opdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)
if args.label is None:
    fname = "%s/%s.dt" % (args.opdir, args.source)
else:
    fname = "%s/%s_%s.dt" % (args.opdir, args.source, args.label)

dm.save_binary(fname)
