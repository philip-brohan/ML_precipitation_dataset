#!/usr/bin/env python

# The whole ERA5 dataset is a bit big to experiment with

# Extract the timeseries for a few selected grid-cells
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
# Define a standard-cube to work with
# Identical to that used in ERA5, except that the longitude cut is moved
#  to mid pacific (-180) instead of over the UK (0)
resolution = 0.25
xmin = -180
xmax = 180
ymin = -90
ymax = 90
pole_latitude = 90
pole_longitude = 180
npg_longitude = 0
cs = iris.coord_systems.RotatedGeogCS(pole_latitude, pole_longitude, npg_longitude)
lat_values = np.arange(ymin, ymax + resolution, resolution)
latitude = iris.coords.DimCoord(
    lat_values, standard_name="latitude", units="degrees_north", coord_system=cs
)
lon_values = np.arange(xmin, xmax, resolution)
longitude = iris.coords.DimCoord(
    lon_values, standard_name="longitude", units="degrees_east", coord_system=cs
)
dummy_data = np.zeros((len(lat_values), len(lon_values)))
sCube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

# Select the points - I can't be bothered to do argparse, just edit this file
# Not more than 25 points
points_x = [403,463,464,467,476,477,478,578]
points_y = [835,835,835,842,916,919,919,919]

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

args = parser.parse_args()


# Load the raw data
random_points = []
raw = []
for year in range(args.startyear, args.endyear + 1):
    m = load_monthly.load(
        organisation="ERA5", year=year, month=args.month,
    ).regrid(sCube,iris.analysis.Nearest())
    if len(raw) == 0:
        for i in range(len(points_x)):
            raw.append([])
    pm = args.month - 1
    if pm < 1:
        pm = 12
    pm = load_monthly.load(
        organisation="ERA5", year=year, month=pm,
    )
    pp = args.month + 1
    if pp > 12:
        pp = 1
    pp = load_monthly.load(
        organisation="ERA5", year=year, month=pp,
    )
    for i in range(len(points_x)):
        raw[i].append(m.data[points_x[i], points_y[i]])
        if points_x[i] > 0:
            raw[i].append(m.data[points_x[i] - 1, points_y[i]])
        if points_x[i] < m.data.shape[0]:
            raw[i].append(m.data[points_x[i] + 1, points_y[i]])
        if points_y[i] > 0:
            raw[i].append(m.data[points_x[i], points_y[i] - 1])
        if points_y[i] < m.data.shape[1]:
            raw[i].append(m.data[points_x[i], points_y[i] + 1])
        raw[i].append(pm.data[points_x[i], points_y[i]])
        raw[i].append(pp.data[points_x[i], points_y[i]])

# Save the data sample
with open("selected.pkl", "wb") as opf:
    pickle.dump((random_points, raw), opf)
