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
    get_month, args.start_year, args.end_year, samples=args.samples
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
