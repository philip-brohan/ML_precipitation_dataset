#!/usr/bin/env python

# Get global mean series of normalized values and store as pickle
# This version works on the zarr-only adjusted datasets

import os
import iris
import numpy as np
import zarr

import pickle
from utilities.grids import E5sCube_grid_areas

rng = np.random.default_rng()

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--label",
    help="Model label",
    type=str,
    required=True,
    default=None,
)
parser.add_argument(
    "--rchoice",
    help="Area reduction choice (None or 'area')",
    type=str,
    required=False,
    default=None,
)
parser.add_argument(
    "--mask_file",
    help="File containing averaging data mask",
    type=str,
    required=False,
    default=None,
)
parser.add_argument(
    "--startyear",
    type=int,
    required=False,
    default=1950,
)
parser.add_argument(
    "--endyear",
    type=int,
    required=False,
    default=2023,
)
args = parser.parse_args()

# Load the mask file if provided
if args.mask_file is not None:
    mask = iris.load_cube(
        "%s/visualizations/time_series/masks/%s.nc"
        % (os.getenv("PDIR"), args.mask_file)
    )


def latlon_reduce(choice, ndata):
    ndata[~np.isfinite(ndata)] = 0
    if args.mask_file is not None:
        ndata[mask.data == 0] = 0
    if choice is None:
        ndata = ndata.flatten()
        ndata = ndata[ndata != 0]
        return np.mean(ndata)
    elif choice == "area":
        gweight = E5sCube_grid_areas
        gweight = np.ma.MaskedArray(gweight, ndata == 0)
        ndata_sum = np.sum(ndata * gweight)
        gweight_sum = np.sum(gweight)
        ndata_mean = ndata_sum / gweight_sum
        return ndata_mean
    else:
        raise Exception("Unsupported latlon_reduce choice %s" % choice)


# Load adjustments and adjusted target
adjustments = {}
adjusted = {}
fn = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/adjusted_target/adjusted_zarr"
adjusted_z = zarr.open(fn, mode="r")
adjusted_fy = adjusted_z.attrs["FirstYear"]
fn2 = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/adjusted_target/adjustments_zarr"
adjustments_z = zarr.open(fn2, mode="r")
for year in range(args.startyear, args.endyear + 1):
    for month in range(1, 13):
        dt = "%04d%02d%03d" % (year, month, 0)
        idx = (year - adjusted_fy) * 12 + (month - 1)
        adjusted_slice = adjusted_z[:, :, idx]
        adjusted[dt] = latlon_reduce(args.rchoice, adjusted_slice)
        adjustments_slice = adjustments_z[:, :, idx]
        adjustments[dt] = latlon_reduce(args.rchoice, adjustments_slice)


if args.rchoice is None:
    args.rchoice = "None"
if args.mask_file is None:
    args.mask_file = "None"
else:
    args.mask_file = os.path.splitext(os.path.basename(args.mask_file))[0]

opdir = "%s/ML_models/xgb_monthly/" % os.getenv("PDIR")
opdir += "/%s/series" % args.label
if not os.path.isdir(opdir):
    os.makedirs(opdir)

with open(
    "%s/%s_%s_%s.pkl" % (opdir, args.mask_file, args.rchoice, "adjustments"), "wb"
) as dfile:
    pickle.dump(adjustments, dfile)
with open(
    "%s/%s_%s_%s.pkl" % (opdir, args.mask_file, args.rchoice, "adjusted"), "wb"
) as dfile:
    pickle.dump(adjusted, dfile)
