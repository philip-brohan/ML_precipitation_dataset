#!/usr/bin/env python

# Make raw data tensors for normalisation

import os
import sys
import argparse
import zarr
import tensorstore as ts
import numpy as np
from get_data.TWCR import TWCR_monthly_load

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


# Output zarr array location
fn = "%s/MLP/raw_datasets/TWCR/%s_zarr" % (
    os.getenv("SCRATCH"),
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
        chunk_layout=ts.ChunkLayout(chunk_shape=[721, 1440, 1, 1]),
        create=True,
        fill_value=np.nan,
        shape=[
            721,
            1440,
            len(TWCR_monthly_load.members),
            date_to_index(LastYear, 12) + 1,
        ],
    ).result()
except ValueError as e:  # Already exists
    pass

# Add date range to array as metadata
# TensorStore doesn't support metadata, so use the underlying zarr array
zarr_ds = zarr.open(fn, mode="r+")
zarr_ds.attrs["FirstYear"] = FirstYear
zarr_ds.attrs["LastYear"] = LastYear

for member_idx in range(len(TWCR_monthly_load.members)):
    for year in range(FirstYear, LastYear + 1):
        for month in range(1, 13):
            idx = date_to_index(year, month)
            slice = zarr_ds[:, :, member_idx, idx]
            if np.all(np.isnan(slice)):  # Data missing, so make it
                cmd = (
                    "%s/make_training_tensor.py --year=%04d --month=%02d --variable=%s --member_idx=%d"
                    % (
                        sDir,
                        year,
                        month,
                        args.variable,
                        member_idx,
                    )
                )
                print(cmd)
