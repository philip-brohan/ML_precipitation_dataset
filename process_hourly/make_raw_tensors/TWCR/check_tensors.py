#!/usr/bin/env python

# Check the raw tensor zarr array

import os
import argparse
import zarr
import numpy as np
import datetime
from get_data_hourly.TWCR import TWCR_hourly_load

from tensor_utils import date_to_index

sDir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--variable",
    help="Variable name",
    type=str,
    required=True,
)
parser.add_argument(
    "--month",
    help="Restrict to selected month",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--day",
    help="Restrict to selected day of month",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--hour",
    help="Restrict to selected hour of day",
    type=int,
    required=False,
    default=None,
)
args = parser.parse_args()

# Find the raw_tensor zarr array
fn = "%s/MLP/raw_datasets_hourly/TWCR/%s_zarr" % (
    os.getenv("PDIR"),
    args.variable,
)

# Add date range to array as metadata
zarr_ds = zarr.open(fn, mode="r+")

count = 0
bad = 0
missing = 0
for year in range(1961, 1990 + 1):
    for month in range(1, 13):
        if args.month is not None and month != args.month:
            continue
        for day in range(1, 32):
            if args.day is not None and day != args.day:
                continue
            for hour in range(0, 24, 3):
                if args.hour is not None and hour != args.hour:
                    continue
                try:
                    dte = datetime.datetime(year, month, day, hour)
                    idx = date_to_index(year, month, day, hour)
                    for member_idx in range(len(TWCR_hourly_load.members)):
                        count += 1
                        try:
                            slice = zarr_ds[:, :, member_idx, idx]
                            if np.any(np.isnan(slice)):
                                print(
                                    "Bad data for %04d-%02d-%02d:%02d_%02d %d"
                                    % (year, month, day, hour, member_idx, idx)
                                )
                                bad += 1
                        except Exception as e:
                            print(
                                "Missing data for %04d-%02d-%02d:%02d_%02d %d"
                                % (year, month, day, hour, member_idx, idx)
                            )
                            missing += 1
                except ValueError as e:
                    pass


print(args.variable)
print("Missing member-hours:", missing)
print("Bad member-hours:", bad)
print("Total member-hours:", count)
print("\n")
