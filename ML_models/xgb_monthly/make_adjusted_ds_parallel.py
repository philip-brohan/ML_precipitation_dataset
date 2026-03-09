#!/usr/bin/env python

# Make smoothed difference field from target and model, and make adjusted target by removing the smoothed difference from the target
# This script does 1 month at a time, and is designed to be run in parallel across months.

import os
import zarr
import numpy as np
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
    "--label",  # name for this validation run
    type=str,
    required=True,
    default=None,
)
parser.add_argument(
    "--target",
    type=str,  # 'TWCR','ERA5','GC5','GPCC','CRU','GPCP'
    required=True,
    default=None,
)
parser.add_argument(
    "--convolve",
    help="Convolution filter - latxlonxtime",
    type=str,
    required=False,
    default=None,
)
args = parser.parse_args()

# Create the output zarr arrays if they don't exist
nIdx = (args.end_year - args.start_year + 1) * 12
shape = (721, 1440, nIdx)
chunks = (721, 1440, 1)
fn = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/adjusted_target/adjustments_zarr"
adjustments_ds = zarr.open(
    fn, mode="w", shape=shape, chunks=chunks, dtype=np.float32, fill_value=np.nan
)
adjustments_ds.attrs["FirstYear"] = args.start_year
adjustments_ds.attrs["LastYear"] = args.end_year

fn = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/adjusted_target/adjusted_zarr"
adjusted_ds = zarr.open(
    fn, mode="w", shape=shape, chunks=chunks, dtype=np.float32, fill_value=np.nan
)
adjusted_ds.attrs["FirstYear"] = args.start_year
adjusted_ds.attrs["LastYear"] = args.end_year


def date_to_index(year, month):
    return (year - args.start_year) * 12 + month - 1


for year in range(args.start_year, args.end_year + 1):
    for month in range(1, 13):
        idx = date_to_index(year, month)
        slice = adjustments_ds[:, :, idx]
        if np.all(np.isnan(slice)):  # Data missing, so make it
            print(
                "./make_adjusted_ds.py --convolve=%s --target=%s --year=%04d --month=%d --label=%s "
                % (args.convolve, args.target, year, month, args.label)
            )
