#!/usr/bin/env python

# Update the raw tensor zarr array with metadata giving dates and indices for each field present

import os
import argparse
import zarr
import numpy as np
import datetime
from get_data_hourly.TWCR import TWCR_hourly_load

from tensor_utils import date_to_index, FirstYear, LastYear

sDir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--variable",
    help="Variable name",
    type=str,
    required=True,
)
args = parser.parse_args()

# Find the raw_tensor zarr array
fn = "%s/MLP/raw_datasets_hourly/TWCR/%s_zarr" % (
    os.getenv("SCRATCH"),
    args.variable,
)

# Add date range to array as metadata
print
zarr_ds = zarr.open(fn, mode="r+")

AvailableHours = {}
start = LastYear
end = FirstYear
for year in range(1961, 1990 + 1):
    for month in range(1, 13):
        for day in range(1, 32):
            for hour in range(0, 24, 3):
                try:
                    dte = datetime.datetime(year, month, day, hour)
                    idx = date_to_index(year, month, day, hour)
                    for member_idx in range(len(TWCR_hourly_load.members)):
                        slice = zarr_ds[:, :, member_idx, idx]
                        if not np.all(np.isnan(slice)):
                            AvailableHours[
                                "%d-%02d-%02d:%02d_%02d"
                                % (year, month, day, hour, member_idx)
                            ] = idx
                            if dte < start:
                                start = dte
                            if dte > end:
                                end = dte
                except ValueError as e:
                    pass
zarr_ds.attrs["AvailableHours"] = AvailableHours

missing = 0
for year in range(1961, 1990 + 1):
    for month in range(1, 13):
        for day in range(1, 32):
            for hour in range(0, 24, 3):
                try:
                    dte = datetime.datetime(year, month, day, hour)
                    if dte < start or dte > end:
                        continue
                    for member_idx in range(len(TWCR_hourly_load.members)):
                        dte = "%d-%02d-%02d:%02d_%02d" % (
                            year,
                            month,
                            day,
                            hour,
                            member_idx,
                        )
                        if dte not in AvailableHours:
                            missing += 1
                except ValueError as e:
                    pass


print(args.variable)
print("Start date:", start)
print("End date:", end)
print("Missing member-hours:", missing)
print("Total member-hours:", len(AvailableHours))
print("\n")
