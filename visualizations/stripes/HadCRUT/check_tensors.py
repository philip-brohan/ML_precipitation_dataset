#!/usr/bin/env python

# Check the  normalized tensor zarr array giving dates and indices for each field present

import os
import zarr
import numpy as np
from get_data.HadCRUT import HadCRUT

from make_raw_tensors.HadCRUT.tensor_utils import date_to_index, FirstYear, LastYear

sDir = os.path.dirname(os.path.realpath(__file__))

# Find the raw_tensor zarr array
fn = "%s/MLP/normalized_datasets/HadCRUT_tf_MM/temperature_zarr" % (
    os.getenv("SCRATCH"),
)

zarr_ds = zarr.open(fn, mode="r+")

AvailableMonths = {}
start = "%04d-%02d" % (LastYear, 12)
end = "%04d-%02d" % (FirstYear, 1)
for year in range(FirstYear, LastYear + 1):
    for month in range(1, 13):
        dte = "%d-%02d" % (year, month)
        idx = date_to_index(year, month)
        for member_idx in range(len(HadCRUT.members)):
            slice = zarr_ds[:, :, member_idx, idx]
            if not np.all(np.isnan(slice)):
                AvailableMonths["%d-%02d_%02d" % (year, month, member_idx)] = idx
                if dte < start:
                    start = dte
                if dte > end:
                    end = dte


missing = 0
for year in range(FirstYear, LastYear + 1):
    for month in range(1, 13):
        if dte < start or dte > end:
            continue
        for member_idx in range(len(HadCRUT.members)):
            dte = "%d-%02d_%02d" % (year, month, member_idx)
            if dte not in AvailableMonths:
                missing += 1


print("Start date:", start)
print("End date:", end)
print("Missing member-months:", missing)
print("Total member-months:", len(AvailableMonths))
print("\n")
