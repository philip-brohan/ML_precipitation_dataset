#!/usr/bin/env python

# Make raw data tensors for normalization

import os
from shutil import rmtree
import argparse
import zarr
import tensorstore as ts
import numpy as np

from tensor_utils import date_to_index, FirstYear, LastYear

sDir = os.path.dirname(os.path.realpath(__file__))

# Create the output zarr array if it doesn't exist
fn = "%s/MLP/raw_datasets/CRU/in_situ/precipitation_zarr" % (os.getenv("SCRATCH"),)

# Create TensorStore dataset if it doesn't exist
try:
    dataset = ts.open(
        {
            "driver": "zarr",
            "kvstore": "file://" + fn,
        },
        dtype=ts.float32,
        chunk_layout=ts.ChunkLayout(chunk_shape=[721, 1440, 1]),
        create=True,
        fill_value=np.nan,
        shape=[
            721,
            1440,
            date_to_index(LastYear, 12) + 1,
        ],
    ).result()
except ValueError:  # Already exists
    pass

# Add date range to array as metadata
# TensorStore doesn't support metadata, so use the underlying zarr array
zarr_ds = zarr.open(fn, mode="r+")
zarr_ds.attrs["FirstYear"] = FirstYear
zarr_ds.attrs["LastYear"] = LastYear

count = 0
for year in range(FirstYear, LastYear + 1):
    for month in range(1, 13):
        idx = date_to_index(year, month)
        slice = zarr_ds[:, :, idx]
        if np.all(np.isnan(slice)):  # Data missing, so make it
            cmd = "%s/make_training_tensor.py --year=%04d --month=%02d" % (
                sDir,
                year,
                month,
            )
            print(cmd)
