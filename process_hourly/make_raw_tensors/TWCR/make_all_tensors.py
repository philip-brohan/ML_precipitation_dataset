#!/usr/bin/env python

# Make raw data tensors for normalisation

import os
import sys
import argparse
import zarr
import tensorstore as ts
import numpy as np
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
parser.add_argument(
    "--member",
    help="member number",
    type=int,
    required=False,
    default=None,
)
args = parser.parse_args()


# Output zarr array location
fn = "%s/MLP/raw_datasets_hourly/TWCR/%s_zarr" % (
    os.getenv("PDIR"),
    args.variable,
)

# Create TensorStore dataset if it doesn't exist
try:
    dataset = ts.open(
        {
            "driver": "zarr",
            "kvstore": "file://" + fn,
        },
        dtype=ts.float32,
        chunk_layout=ts.ChunkLayout(chunk_shape=[256, 512, 1, 1]),
        create=True,
        fill_value=np.nan,
        shape=[
            256,
            512,
            len(TWCR_hourly_load.members),
            date_to_index(LastYear.year, LastYear.month, LastYear.day, LastYear.hour)
            + 1,
        ],
    ).result()
except ValueError as e:  # Already exists
    pass

# Add date range to array as metadata
# TensorStore doesn't support metadata, so use the underlying zarr array
zarr_ds = zarr.open(fn, mode="r+")
zarr_ds.attrs["FirstYear"] = FirstYear.isoformat()
zarr_ds.attrs["LastYear"] = LastYear.isoformat()

for member_idx in range(len(TWCR_hourly_load.members)):
    if args.member is not None and member_idx != args.member:
        continue
    # for year in range(FirstYear.year, LastYear.year + 1):
    for year in range(1961, 1990 + 1):
        for month in range(1, 13):
            for day in range(1, 32):
                for hour in range(0, 24, 3):
                    try:
                        idx = date_to_index(year, month, day, hour)
                        slice = zarr_ds[:, :, member_idx, idx]
                        if np.all(np.isnan(slice)):  # Data missing, so make it
                            cmd = (
                                "%s/make_training_tensor.py --year=%04d --month=%02d --day=%02d --hour=%02d --variable=%s --member_idx=%d"
                                % (
                                    sDir,
                                    year,
                                    month,
                                    day,
                                    hour,
                                    args.variable,
                                    member_idx,
                                )
                            )
                            print(cmd)
                    except Exception as e:
                        # print(e)
                        pass
