#!/usr/bin/env python

# Plot maps of the three parameters in the gamma normalisation fit
# For a specified month - shape, location, and scale.

import os
import sys
import iris
import iris.time
import numpy as np

from utilities import plots, grids
from get_data.ERA5 import ERA5_monthly

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean
import argparse

# I don't care about datums.
iris.FUTURE.datum_support = True

parser = argparse.ArgumentParser()
parser.add_argument(
    "--month", help="Month to plot", type=int, required=False, default=3
)
parser.add_argument(
    "--variable",
    help="Name of variable to use (mean_sea_level_pressure, total_precipitation, ...)",
    type=str,
    default="total_precipitation",
)
args = parser.parse_args()

if args.variable == "sea_surface_temperature":
    mask = ERA5_monthly.load("land_mask", grid=grids.E5sCube)

# Load the fitted values
shape = iris.load_cube(
    "%s/MLP/normalisation/SPI_monthly/ERA5_tf_MM/%s/shape_m%02d.nc"
    % (os.getenv("SCRATCH"), args.variable, args.month),
)
location = iris.load_cube(
    "%s/MLP/normalisation/SPI_monthly/ERA5_tf_MM/%s/location_m%02d.nc"
    % (os.getenv("SCRATCH"), args.variable, args.month),
)
scale = iris.load_cube(
    "%s/MLP/normalisation/SPI_monthly/ERA5_tf_MM/%s/scale_m%02d.nc"
    % (os.getenv("SCRATCH"), args.variable, args.month),
)
if args.variable == "sea_surface_temperature":
    shape.data = np.ma.masked_where(mask.data == 0, shape.data)
    location.data = np.ma.masked_where(mask.data == 0, location.data)
    scale.data = np.ma.masked_where(mask.data == 0, scale.data)

# Make the plot
fig = Figure(
    figsize=(10, 10 * 3 / 2),
    dpi=100,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
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
axb = fig.add_axes([0, 0, 1, 1])
axb.set_axis_off()
axb.add_patch(
    Rectangle(
        (0, 0),
        1,
        1,
        facecolor=(1.0, 1.0, 1.0, 1),
        fill=True,
        zorder=1,
    )
)


ax_location = fig.add_axes([0.02, 0.68, 0.8, 0.31])
location_img = plots.plotFieldAxes(
    ax_location,
    location,
    cMap=cmocean.cm.balance,
)
ax_location_cb = fig.add_axes([0.85, 0.68, 0.13, 0.31])
ax_location_cb.set_axis_off()
cb = fig.colorbar(
    location_img,
    ax=ax_location_cb,
    location="right",
    orientation="vertical",
    fraction=1.0,
)

ax_scale = fig.add_axes([0.02, 0.345, 0.8, 0.31])
scale_img = plots.plotFieldAxes(
    ax_scale,
    scale,
    cMap=cmocean.cm.balance,
)
ax_scale_cb = fig.add_axes([0.85, 0.345, 0.13, 0.31])
ax_scale_cb.set_axis_off()
cb = fig.colorbar(
    scale_img, ax=ax_scale_cb, location="right", orientation="vertical", fraction=1.0
)

ax_shape = fig.add_axes([0.02, 0.01, 0.8, 0.31])
shape_img = plots.plotFieldAxes(
    ax_shape,
    shape,
    cMap=cmocean.cm.balance,
)
ax_shape_cb = fig.add_axes([0.85, 0.01, 0.13, 0.31])
ax_shape_cb.set_axis_off()
cb = fig.colorbar(
    shape_img, ax=ax_shape_cb, location="right", orientation="vertical", fraction=1.0
)

fig.savefig("gamma.png")
