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
    "--source",
    type=str,  # 'TWCR','ERA5', or 'GC5'
    required=True,
    default=None,
)
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--no_uwind", action="store_true")
parser.add_argument("--no_vwind", action="store_true")
parser.add_argument("--no_humidity", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
parser.add_argument("--lat_offset", type=int, required=False, default=5)
parser.add_argument("--lon_offset", type=int, required=False, default=5)

args = parser.parse_args()

# Load the data entry function - source specific
if args.source == "TWCR":
    from TWCR import get_month
elif args.source == "ERA5":
    from ERA5 import get_month
elif args.source == "GC5":
    from GC5 import get_month

# Source is a n*5 array containing 5 features:
#  pressure, temperature, latitude, longitude, month (all normalised)
# Target is an n*1 array containing one feature:
#  precipitation (normalised)

source, target = get_source_and_target(
    get_month,
    args.start_year,
    args.end_year,
    samples=args.samples,
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

dm = to_DMatrix(source, target)

# Save the files as xgboost DMatrix native
opdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")
if not os.path.isdir(opdir):
    os.makedirs(opdir)
if args.label is None:
    fname = "%s/%s.dt" % (opdir, args.source)
else:
    fname = "%s/%s_%s.dt" % (opdir, args.source, args.label)

dm.save_binary(fname)
