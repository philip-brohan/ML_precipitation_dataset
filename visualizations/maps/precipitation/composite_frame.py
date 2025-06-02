#!/usr/bin/env python

# Plot a 3-way composite map - with uncertainty fog
# TWCR, CRU, and GPCC.

import os
import sys
import math
import numpy as np
import zarr

from utilities.grids import E5sCube

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from utilities import plots, grids
import cmocean

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--year",
    type=int,
    required=True,
)
parser.add_argument(
    "--month",
    type=int,
    required=True,
)
args = parser.parse_args()

opdir = "%s/MLP/visualizations/maps/composite" % (os.getenv("PDIR"),)
if not os.path.isdir(opdir):
    os.makedirs(opdir)

# Colourmap
cmap = cmocean.cm.balance

# Get data for selected month - cru
fn = "%s/MLP/normalized_datasets/CRU_tf_MM/precipitation_zarr" % (os.getenv("PDIR"),)
zarr_array = zarr.open(fn, mode="r")
AvailableMonths = zarr_array.attrs["AvailableMonths"]
data_cru = zarr_array[:, :, AvailableMonths["%04d-%02d" % (args.year, args.month)]]
del zarr_array
# - GPCC
fn = "%s/MLP/normalized_datasets/GPCC_tf_MM/precipitation_zarr" % (os.getenv("PDIR"),)
zarr_array = zarr.open(fn, mode="r")
AvailableMonths = zarr_array.attrs["AvailableMonths"]
data_gpcc = zarr_array[:, :, AvailableMonths["%04d-%02d" % (args.year, args.month)]]
del zarr_array
# - TWCR
fn = "%s/MLP/normalized_datasets/TWCR_tf_MM/PRATE_zarr" % (os.getenv("PDIR"),)
zarr_array = zarr.open(fn, mode="r")
AvailableMonths = zarr_array.attrs["AvailableMonths"]
idx = AvailableMonths["%04d-%02d_01" % (args.year, args.month)]
data_twcr = zarr_array[:, :, :, idx]
del zarr_array

# Make a mean field
data_mean = np.mean([data_cru, data_gpcc, np.mean(data_twcr, axis=2)], axis=0)
data_mean = np.where(data_cru == 0.0, 0.0, data_mean)
data_mean = np.where(data_gpcc == 0.0, 0.0, data_mean)
dmc = E5sCube.copy()
dmc.data = np.ma.masked_where(data_mean == 0, data_mean)

# Make a spread field
data_spread = np.std([data_cru, data_gpcc, np.mean(data_twcr, axis=2)], axis=0)
data_spread = np.where(data_cru == 0.0, 0.0, data_spread)
data_spread = np.where(data_gpcc == 0.0, 0.0, data_spread)
dsc = E5sCube.copy()
dsc.data = np.ma.masked_where(data_spread == 0, data_spread)

fig = Figure(
    figsize=(20, 10),
    dpi=300,
    facecolor=(0.7, 0.7, 0.7, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=True,
    subplotpars=None,
    tight_layout=None,
)
canvas = FigureCanvas(fig)
font = {
    "family": "sans-serif",
    "sans-serif": "Arial",
    "weight": "normal",
    "size": 20,
}
matplotlib.rc("font", **font)

lats = dsc.coord("grid_latitude").points
lons = dsc.coord("grid_longitude").points

ax_field = fig.add_axes([0.0, 0.0, 1.0, 1.0])

# Land mask - strictly CRU coverage, rather than land
mask_img = ax_field.pcolorfast(
    lons,
    lats,
    dmc.data,
    cmap=matplotlib.colors.ListedColormap(((0.4, 0.4, 0.4, 0), (0.4, 0.4, 0.4, 1.0))),
    vmin=0,
    vmax=0.0001,
    alpha=1,
    zorder=10,
)

# Plot the cross-dataset standard deviations
T_img = ax_field.pcolorfast(
    lons,
    lats,
    dsc.data,
    cmap="viridis",
    vmin=0.0,
    vmax=0.25,
    alpha=1.0,
    zorder=10,
)

# Add spread-based stipling
# stippling_mask = dsc.data > 0.25
# X, Y = np.meshgrid(lons, lats)
# ax_field.scatter(
#     X[stippling_mask], Y[stippling_mask], color="black", s=0.025, zorder=100
# )


# Label with the date
ax_field.text(
    180 - 360 * 0.009,
    90 - 180 * 0.016,
    "%04d-%02d" % (args.year, args.month),
    horizontalalignment="right",
    verticalalignment="top",
    color="black",
    bbox=dict(
        facecolor=(0.6, 0.6, 0.6, 0.5), edgecolor="black", boxstyle="round", pad=0.5
    ),
    size=18,
    clip_on=True,
    zorder=500,
)

fig.savefig("%s/%04d-%02d.webp" % (opdir, args.year, args.month))
