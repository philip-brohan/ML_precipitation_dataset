#!/usr/bin/env python

# Time series validation is a bit slow - run it in parallel
# This script prints out a series of scripts to be run on SPICE


import os
import zarr
import tensorstore as ts
import numpy as np

opdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--mlabel",
    type=str,
    required=True,
)
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--no_uwind", action="store_true")
parser.add_argument("--no_vwind", action="store_true")
parser.add_argument("--no_humidity", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
parser.add_argument("--lat_offset", type=int, required=False, default=None)
parser.add_argument("--lon_offset", type=int, required=False, default=None)
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
    "--source",
    type=str,  # 'TWCR','ERA5', or 'GC5'
    required=True,
    default=None,
)
parser.add_argument(
    "--target",
    type=str,  # 'TWCR','ERA5','GC5','GPCC','CRU','GPCP'
    required=True,
    default=None,
)
args = parser.parse_args()
if args.target is None:
    args.target = args.source


def date_to_index(year, month):
    return (year - args.start_year) * 12 + month - 1


# Create the output zarr array if it doesn't exist
fn = "%s/%s/ts_validation/model_zarr" % (opdir, args.label)

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
            date_to_index(args.end_year, 12) + 1,
        ],
    ).result()
except ValueError:  # Already exists
    pass

# Add date range to array as metadata
# TensorStore doesn't support metadata, so use the underlying zarr array
zarr_ds = zarr.open(fn, mode="r+")
zarr_ds.attrs["FirstYear"] = args.start_year
zarr_ds.attrs["LastYear"] = args.end_year

for year in range(args.start_year, args.end_year + 1):
    for month in range(1, 13):
        idx = date_to_index(year, month)
        slice = zarr_ds[:, :, idx]
        if np.all(np.isnan(slice)):  # Data missing, so make it
            print(
                "./validate_time_series.py --source=%s --target=%s --year=%04d --month=%d --label=%s "
                % (args.source, args.target, year, month, args.label),
                end="",
            )
            print("--mlabel=%s " % args.mlabel, end="")
            if args.no_pressure:
                print("--no_pressure ", end="")
            if args.no_temperature:
                print("--no_temperature ", end="")
            if args.no_uwind:
                print("--no_uwind ", end="")
            if args.no_vwind:
                print("--no_vwind ", end="")
            if args.no_humidity:
                print("--no_humidity ", end="")
            if args.fix_month is not None:
                print("--fix_month=%s " % args.fix_month, end="")
            if args.lat_offset is not None:
                print("--lat_offset=%s " % args.lat_offset, end="")
            if args.fix_lat is not None:
                print("--fix_lat=%s " % args.fix_lat, end="")
            if args.lon_offset is not None:
                print("--lon_offset=%s " % args.lon_offset, end="")
            if args.fix_lon is not None:
                print("--fix_lon=%s " % args.fix_lon, end="")
            print("")  # add \n
