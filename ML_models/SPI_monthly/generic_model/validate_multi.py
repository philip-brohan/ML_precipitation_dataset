#!/usr/bin/env python

# Plot validation statistics for all the test cases

import os
import sys
import numpy as np
import tensorflow as tf
import iris
import iris.fileformats
import iris.analysis
import datetime

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

from specify import specification

# I don't need all the messages about a missing font
import logging

logging.getLogger("matplotlib.font_manager").disabled = True


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--epoch", help="Epoch", type=int, required=False, default=250)
parser.add_argument(
    "--startyear", help="First year to plot", type=int, required=False, default=None
)
parser.add_argument(
    "--endyear", help="Last year to plot", type=int, required=False, default=None
)
parser.add_argument(
    "--min_lat",
    help="Minimum latitude for target region (-90 to 90)",
    type=float,
    required=False,
    default=-90,
)
parser.add_argument(
    "--max_lat",
    help="Maximum latitude for target region (-90 to 90)",
    type=float,
    required=False,
    default=90,
)
parser.add_argument(
    "--min_lon",
    help="Minimum longitude for target region (-180 to 180)",
    type=float,
    required=False,
    default=-180,
)
parser.add_argument(
    "--max_lon",
    help="Maximum longitude for target region (-180 to 180)",
    type=float,
    required=False,
    default=180,
)
parser.add_argument(
    "--training",
    help="Use training months (not test months)",
    dest="training",
    default=False,
    action="store_true",
)
args = parser.parse_args()

from utilities import grids

from ML_models.SPI_monthly.generic_model.makeDataset import getDataset
from ML_models.SPI_monthly.generic_model.autoencoderModel import DCVAE, getModel

# Set up the test data
purpose = "Test"
if args.training:
    purpose = "Train"
dataset = getDataset(specification, purpose=purpose)
dataset = dataset.batch(1)

autoencoder = getModel(specification, args.epoch)


def tensor_to_cube(t):
    result = grids.E5sCube.copy()
    result.data = np.squeeze(t.numpy())
    result.data = np.ma.masked_where(result.data == 0.0, result.data, copy=False)
    return result


def field_to_scalar(field):
    field = field.extract(
        iris.Constraint(
            coord_values={
                "grid_latitude": lambda cell: args.min_lat <= cell <= args.max_lat
            }
        )
        & iris.Constraint(
            coord_values={
                "grid_longitude": lambda cell: args.min_lon <= cell <= args.max_lon
            }
        )
    )
    return np.mean(field.data)


nFields = specification["nOutputChannels"]


# Get target and encoded statistics for one test case
def compute_stats(model, x):
    # get the date from the filename tensor
    dateStr = tf.strings.split(x[0][0][0], sep="/")[-1].numpy()
    year = int(dateStr[:4])
    month = int(dateStr[5:7])
    dtp = datetime.date(year, month, 15)
    # Pass the test field through the autoencoder
    generated = model.call(x, training=False)

    stats = {}
    stats["dtp"] = dtp
    stats["target"] = {}
    stats["generated"] = {}
    for varI in range(nFields):
        stats["target"][specification["outputNames"][varI]] = field_to_scalar(
            tensor_to_cube(tf.squeeze(x[-1][:, :, :, varI])),
        )
        stats["generated"][specification["outputNames"][varI]] = field_to_scalar(
            tensor_to_cube(tf.squeeze(generated[:, :, :, varI])),
        )
    return stats


all_stats = {}
all_stats["dtp"] = []
all_stats["target"] = {}
all_stats["generated"] = {}
for case in dataset:
    stats = compute_stats(autoencoder, case)
    all_stats["dtp"].append(stats["dtp"])
    for key in stats["target"].keys():
        if key in all_stats["target"]:
            all_stats["target"][key].append(stats["target"][key])
            all_stats["generated"][key].append(stats["generated"][key])
        else:
            all_stats["target"][key] = [stats["target"][key]]
            all_stats["generated"][key] = [stats["generated"][key]]


figScale = 3.0
wRatios = (3, 1.25)

# Make the plot
fig = Figure(
    figsize=(figScale * sum(wRatios), figScale * nFields),
    dpi=300,
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
    "size": 14,
}
matplotlib.rc("font", **font)
axb = fig.add_axes([0, 0, 1, 1])
axb.add_patch(
    Rectangle(
        (0, 0),
        1,
        1,
        facecolor=(0.95, 0.95, 0.95, 1),
        fill=True,
        zorder=1,
    )
)


# Plot a variable in its subfigure
def plot_var(sfig, ts, t, m, label):
    # Get two axes in the subfig
    var_axes = sfig.subplots(nrows=1, ncols=2, width_ratios=wRatios, squeeze=False)

    # Calculate y range
    ymin = min(min(t), min(m))
    ymax = max(max(t), max(m))
    ypad = (ymax - ymin) * 0.1
    if ypad == 0:
        ypad = 1

    # First subaxis for time-series plot
    var_axes[0, 0].set_xlim(
        ts[0] - datetime.timedelta(days=15), ts[-1] + datetime.timedelta(days=15)
    )
    var_axes[0, 0].set_ylim(ymin - ypad, ymax + ypad)
    var_axes[0, 0].grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
    var_axes[0, 0].text(
        ts[0] - datetime.timedelta(days=15),
        ymax + ypad,
        label,
        ha="left",
        va="top",
        bbox=dict(boxstyle="square,pad=0.5", fc=(1, 1, 1, 1)),
        zorder=100,
    )
    var_axes[0, 0].add_line(
        Line2D(ts, t, linewidth=2, color=(0, 0, 0, 1), alpha=1.0, zorder=50)
    )
    var_axes[0, 0].add_line(
        Line2D(ts, m, linewidth=2, color=(1, 0, 0, 1), alpha=1.0, zorder=60)
    )

    # Second subaxis for scatter plot
    var_axes[0, 1].set_xlim(ymin - ypad, ymax + ypad),
    var_axes[0, 1].set_ylim(ymin - ypad, ymax + ypad),
    var_axes[0, 1].grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
    var_axes[0, 1].scatter(t, m, s=2, color=(1, 0, 0, 1), zorder=60)
    var_axes[0, 1].add_line(
        Line2D(
            (ymin - ypad, ymax + ypad),
            (ymin - ypad, ymax + ypad),
            linewidth=1,
            color=(0, 0, 0, 1),
            alpha=0.2,
            zorder=10,
        )
    )


# Each variable in its own subfig
subfigs = fig.subfigures(nFields, 1, wspace=0.01)
for varI in range(nFields):
    vName = specification["outputNames"][varI]
    plot_var(
        subfigs[varI],
        all_stats["dtp"],
        all_stats["target"][vName],
        all_stats["generated"][vName],
        vName,
    )


fig.savefig("multi.png")
