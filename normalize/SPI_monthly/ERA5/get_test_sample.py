#!/usr/bin/env python

# The whole ERA5 dataset is a bit big to experiment with

# Extract the timeseries for a few random grid-cells
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
    "--month", help="Month to extract", type=int, required=False, default=3
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
    m = load_monthly.load(
        organisation="ERA5", year=year, month=args.month, constraint=llconstraint
    )
    if len(raw) == 0:
        random_i = rng.choice(range(m.data.shape[0]), size=args.nsample, replace=False)
        random_j = rng.choice(range(m.data.shape[1]), size=args.nsample, replace=False)
        for i in range(args.nsample):
            raw.append([])
    pm = args.month - 1
    if pm < 1:
        pm = 12
    pm = load_monthly.load(
        organisation="ERA5", year=year, month=pm, constraint=llconstraint
    )
    pp = args.month + 1
    if pp > 12:
        pp = 1
    pp = load_monthly.load(
        organisation="ERA5", year=year, month=pp, constraint=llconstraint
    )
    for i in range(args.nsample):
        raw[i].append(m.data[random_i[i], random_j[i]])
        if random_i[i] > 0:
            raw[i].append(m.data[random_i[i] - 1, random_j[i]])
        if random_i[i] < m.data.shape[0]:
            raw[i].append(m.data[random_i[i] + 1, random_j[i]])
        if random_j[i] > 0:
            raw[i].append(m.data[random_i[i], random_j[i] - 1])
        if random_j[i] < m.data.shape[1]:
            raw[i].append(m.data[random_i[i], random_j[i] + 1])
        raw[i].append(pm.data[random_i[i], random_j[i]])
        raw[i].append(pp.data[random_i[i], random_j[i]])

# Save the data sample
with open("sample_m%02d.pkl" % args.month, "wb") as opf:
    pickle.dump((random_points, raw), opf)
