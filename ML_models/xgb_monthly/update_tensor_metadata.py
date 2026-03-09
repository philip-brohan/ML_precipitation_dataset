#!/usr/bin/env python

# Update the raw tensor zarr array with metadata giving dates and indices for each field present

import os
import argparse
import zarr
import numpy as np

sDir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--label",
    help="Label",
    type=str,
    required=True,
)
args = parser.parse_args()

# Find the model output zarr array
opdir = f"{os.getenv('PDIR')}/ML_models/xgb_monthly/{args.label}/ts_validation"
fn = "%s/model_zarr" % (opdir,)

# Add date range to array as metadata
zarr_ds = zarr.open(fn, mode="r+")
FirstYear = zarr_ds.attrs["FirstYear"]
LastYear = zarr_ds.attrs["LastYear"]


def date_to_index(year, month):
    idx = (year - FirstYear) * 12 + (month - 1)
    return idx


AvailableMonths = {}
start = "%04d-%02d" % (LastYear, 12)
end = "%04d-%02d" % (FirstYear, 1)
for year in range(FirstYear, LastYear + 1):
    for month in range(1, 13):
        dte = "%d-%02d" % (year, month)
        idx = date_to_index(year, month)
        slice = zarr_ds[:, :, idx]
        if not np.all(np.isnan(slice)):
            AvailableMonths["%d-%02d" % (year, month)] = idx
            if dte < start:
                start = dte
            if dte > end:
                end = dte

zarr_ds.attrs["AvailableMonths"] = AvailableMonths

missing = 0
for year in range(FirstYear, LastYear + 1):
    for month in range(1, 13):
        dte = "%d-%02d" % (year, month)
        if dte < start or dte > end:
            continue
        if dte not in AvailableMonths:
            missing += 1

print(args.label)
print("Start date:", start)
print("End date:", end)
print("Missing months:", missing)
print("Total months:", len(AvailableMonths))
print("\n")
