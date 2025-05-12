#!/usr/bin/env python

# Check the normalized tensor zarr array

import os
import argparse
import zarr
import numpy as np
import datetime
from get_data_hourly.TWCR import TWCR_hourly_load

from process_hourly.make_raw_tensors.TWCR.tensor_utils import date_to_index

sDir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--variable",
    help="Variable name",
    type=str,
    required=True,
)
parser.add_argument(
    "--year",
    help="Restrict to selected year",
    type=int,
    required=False,
    default=None,
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
fn = "%s/MLP/normalized_datasets_hourly/TWCR_tf_MM/%s_zarr" % (
    os.getenv("SCRATCH"),
    args.variable,
)

# Add date range to array as metadata
zarr_ds = zarr.open(fn, mode="r+")

count = 0
bad = 0
missing = 0
for year in range(1961, 1990 + 1):
    if args.year is not None and year != args.year:
        continue
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
                            z_file = "%s/0.0.%d.%d" % (fn, member_idx, idx)
                            if os.path.exists(z_file + ".__lock"):
                                os.rename(z_file + ".__lock", z_file)
                                print("Recovered from lock file")
                            else:
                                missing += 1
                except ValueError as e:
                    pass


print(args.variable)
print("Missing member-hours:", missing)
print("Bad member-hours:", bad)
print("Total member-hours:", count)
print("\n")
