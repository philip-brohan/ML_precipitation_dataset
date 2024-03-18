#!/usr/bin/env python

# The whole ERA5 dataset is a bit big to experiment with

# Extract the monthly timeseries for a few random grid-cells
#  and save them to experiment on.

import os
import sys
import iris
import iris.cube
import iris.util
import iris.time
import argparse
import numpy as np
import pickle

from get_data import load_monthly

from scipy.stats import gamma

rng = np.random.default_rng()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--startyear", help="First year to extract", type=int, required=False, default=1940
)
parser.add_argument(
    "--endyear", help="Last year to extract", type=int, required=False, default=2020
)
parser.add_argument(
    "--min_lat",
    help="Minimum latitude to extract",
    type=float,
    required=False,
    default=-90,
)
parser.add_argument(
    "--max_lat",
    help="Maximum latitude to extract",
    type=float,
    required=False,
    default=90.1,
)
parser.add_argument(
    "--nsample",
    help="Number of sample points to extract",
    type=int,
    default=25,
)
args = parser.parse_args()


llconstraint = iris.Constraint(
    coord_values={"latitude": lambda cell: args.min_lat <= cell < args.max_lat}
)
# Load the raw data
random_points = []
raw = []
for year in range(args.startyear, args.endyear + 1):
    for month in range(1, 13):
        m = load_monthly.load(
            organisation="ERA5", year=year, month=month, constraint=llconstraint
        )
        m = m.data.flatten()
        if len(raw) == 0:
            random_points = rng.choice(range(len(m)), size=args.nsample, replace=False)
            for i in range(args.nsample):
                raw.append([])
        for i in range(args.nsample):
            raw[i].append(m[random_points[i]])

# Save the data sample
with open("sample.pkl", "wb") as opf:
    pickle.dump((random_points, raw), opf)
