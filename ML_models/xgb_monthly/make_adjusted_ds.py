#!/usr/bin/env python

# Make smoothed difference field from target and model, and make adjusted target by removing the smoothed difference from the target
# This script does 1 month at a time, and is designed to be run in parallel across months.

import zarr
import os

import argparse
from astropy.convolution import convolve
import re
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--target", help="Target dataset", type=str, required=True)
parser.add_argument("--label", help="Model label", type=str, required=True)
parser.add_argument(
    "--year", help="Year for the output dataset", type=int, required=True
)
parser.add_argument(
    "--month", help="Month for the output dataset", type=int, required=True
)
parser.add_argument(
    "--convolve",
    help="Convolution filter - latxlonxtime",
    type=str,
    required=False,
    default=None,
)
args = parser.parse_args()

# Create convolution filter
result = re.search(r"(\d+)x(\d+)x(\d+)", args.convolve)
try:
    hv = int(result.groups()[0])
    vv = int(result.groups()[1])
    yv = int(result.groups()[2])
    filter = np.full((vv, hv, yv), 1 / (vv * hv * yv))
    months_padding = yv // 2 + 1
except:
    raise Exception("Unsupported convolution choice %s" % args.convolve)


def year_month_offset(year: int, month: int, offset: int) -> tuple[int, int]:
    total = year * 12 + (month - 1) + offset
    y, m0 = divmod(total, 12)
    return y, m0 + 1


# Load target data
if args.target == "ERA5":
    from ERA5 import get_month
elif args.target == "TWCR":
    from TWCR import get_month
else:
    raise Exception("Unsupported target dataset %s" % args.target)

target = []
for offset in range(-months_padding, months_padding + 1):
    y, m = year_month_offset(int(args.year), int(args.month), offset)
    target.append(get_month("precipitation", y, m))
target = np.stack(target, axis=-1)

# Load model data
fn = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/ts_validation/model_zarr"
zarr_array = zarr.open(fn, mode="r")
AvailableMonths = zarr_array.attrs["AvailableMonths"]
model = []
for offset in range(-months_padding, months_padding + 1):
    y, m = year_month_offset(int(args.year), int(args.month), offset)
    try:
        d_idx = AvailableMonths["%04d-%02d" % (y, m)]
        model.append(zarr_array[:, :, d_idx])
    except KeyError:
        model.append(np.full((721, 1440), np.nan))
model = np.stack(model, axis=-1)

# Make smoothed difference field
diff = target - model
diff_smooth = convolve(diff, filter, boundary="extend")[:, :, months_padding]
# Make adjusted target by removing the smoothed difference
target_adjusted = target[:, :, months_padding] - diff_smooth

# Save the smoothed difference
fn = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/adjusted_target/adjustments_zarr"
zarr_ds = zarr.open(fn, mode="r+")
FirstYear = zarr_ds.attrs["FirstYear"]
idx = (args.year - FirstYear) * 12 + (args.month - 1)
zarr_ds[:, :, idx] = diff_smooth.astype(np.float32)

# Save the adjusted target
fn = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/adjusted_target/adjusted_zarr"
zarr_ds = zarr.open(fn, mode="r+")
FirstYear = zarr_ds.attrs["FirstYear"]
idx = (args.year - FirstYear) * 12 + (args.month - 1)
zarr_ds[:, :, idx] = target_adjusted.astype(np.float32)
