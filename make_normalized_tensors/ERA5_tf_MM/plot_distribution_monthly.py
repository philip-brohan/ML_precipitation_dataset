#!/usr/bin/env python

# Plot raw and normalized variable for a selected month
# Map and distribution.

import os
import sys
import numpy as np


# Supress TensorFlow moaning about cuda - we don't need a GPU for this
# Also the warning message confuses people.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
import zarr

from utilities import plots
from make_normalized_tensors.ERA5_tf_MM.tensor_utils import tensor_to_cube

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--year", help="Year to plot", type=int, required=False, default=1969
)
parser.add_argument(
    "--month", help="Month to plot", type=int, required=False, default=3
)
parser.add_argument(
    "--variable",
    help="Name of variable to use (mean_sea_level_pressure, 2m_temperature, ...)",
    type=str,
    default="total_precipitation",
)
args = parser.parse_args()

fn = "%s/MLP/normalized_datasets/ERA5_tf_MM/%s_zarr" % (
    os.getenv("SCRATCH"),
    args.variable,
)


# Get the raw data
raw_zarr = zarr.open(
    "%s/MLP/raw_datasets/ERA5/%s_zarr"
    % (
        os.getenv("SCRATCH"),
        args.variable,
    ),
    mode="r",
)
AvailableMonths = raw_zarr.attrs["AvailableMonths"]


idx = AvailableMonths["%04d-%02d" % (args.year, args.month)]
raw = tensor_to_cube(tf.convert_to_tensor(raw_zarr[:, :, idx], tf.float32))
raw.data.data[np.isnan(raw.data.data)] = 0
raw.data.mask[raw.data.data == 0] = True

# Get the normalized data
normalized_zarr = zarr.open(
    "%s/MLP/normalized_datasets/ERA5_tf_MM/%s_zarr"
    % (
        os.getenv("SCRATCH"),
        args.variable,
    ),
    mode="r",
)

normalized = tensor_to_cube(
    tf.convert_to_tensor(normalized_zarr[:, :, idx], tf.float32)
)
normalized.data.mask[normalized.data.data == 0] = True

# Make the plot
fig = Figure(
    figsize=(10 * 3 / 2, 10),
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
    "sans-serif": "DejaVu Sans",
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

# choose actual and normalized data colour maps based on variable
cmaps = (cmocean.cm.balance, cmocean.cm.balance)
if args.variable == "total_precipitation":
    cmaps = (cmocean.cm.rain, cmocean.cm.tarn)
if args.variable == "mean_sea_level_pressure":
    cmaps = (cmocean.cm.diff, cmocean.cm.diff)


ax_raw = fig.add_axes([0.02, 0.515, 0.607, 0.455])
if args.variable == "total_precipitation":
    vMin = 0
else:
    vMin = np.percentile(raw.data.compressed(), 5)
plots.plotFieldAxes(
    ax_raw,
    raw,
    vMin=vMin,
    vMax=np.percentile(raw.data.compressed(), 95),
    cMap=cmaps[0],
)

ax_hist_raw = fig.add_axes([0.683, 0.535, 0.303, 0.435])
plots.plotHistAxes(ax_hist_raw, raw, bins=25)

ax_normalized = fig.add_axes([0.02, 0.03, 0.607, 0.455])
plots.plotFieldAxes(
    ax_normalized,
    normalized,
    vMin=-0.25,
    vMax=1.25,
    cMap=cmaps[1],
)

ax_hist_normalized = fig.add_axes([0.683, 0.05, 0.303, 0.435])
plots.plotHistAxes(ax_hist_normalized, normalized, vMin=-0.25, vMax=1.25, bins=25)


fig.savefig("monthly.webp")
