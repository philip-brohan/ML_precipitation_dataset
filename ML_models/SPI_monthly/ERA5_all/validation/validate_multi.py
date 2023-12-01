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
from statistics import mean

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

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

sys.path.append("%s/.." % os.path.dirname(__file__))
from localise import ModelName
from autoencoderModel import DCVAE
from makeDataset import getDataset
from make_tensors.tensor_utils import (
    tensor_to_cube,
    unnormalise,
    sCube,
)


# Set up the test data
purpose = "test"
if args.training:
    purpose = "training"
testData = getDataset(
    purpose=purpose, startyear=args.startyear, endyear=args.endyear, shuffle=False
)
testData = testData.batch(1)

autoencoder = DCVAE()
weights_dir = "%s/MLP/%s/weights/Epoch_%04d" % (
    os.getenv("SCRATCH"),
    ModelName,
    args.epoch,
)
load_status = autoencoder.load_weights("%s/ckpt" % weights_dir)
load_status.assert_existing_objects_matched()


def field_to_scalar(field, month, normalised=False):
    if normalised:
        field = unnormalise(field,month)
    field = field.extract(
        iris.Constraint(
            coord_values={"latitude": lambda cell: args.min_lat <= cell <= args.max_lat}
        )
        & iris.Constraint(
            coord_values={
                "longitude": lambda cell: args.min_lon <= cell <= args.max_lon
            }
        )
    )
    return np.mean(field.data)


# Get target and encoded statistics for one test case
def compute_stats(model, x):
    # get the date from the filename tensor
    fn = x[1].numpy()[0]
    year = int(fn[:4])
    month = int(fn[5:7])
    dtp = datetime.date(year, month, 15)
    # Pass the test field through the autoencoder
    generated = model.call(x[0], training=False)

    stats = {}
    stats["dtp"] = dtp
    stats["n_target"] = field_to_scalar(
        tensor_to_cube(tf.squeeze(x[0])),
        month,
        normalised=False,
    )
    stats["n_model"] = field_to_scalar(
        tensor_to_cube(tf.squeeze(generated)),
        month,
        normalised=False,
    )
    stats["r_target"] = field_to_scalar(
        tensor_to_cube(tf.squeeze(x[0])),
        month,
        normalised=True,
    )
    stats["r_model"] = field_to_scalar(
        tensor_to_cube(tf.squeeze(generated)),
        month,
        normalised=True,
    )
    return stats


all_stats = {}
for case in testData:
    stats = compute_stats(autoencoder, case)
    for key in stats.keys():
        if key in all_stats:
            all_stats[key].append(stats[key])
        else:
            all_stats[key] = [stats[key]]


# Plot sizes
tsh = 2
ssh = 2
tsw = 4
ssw = 2
hpad = 0.5
wpad = 0.5
fig_h = tsh * 2 + hpad * 3
fig_w = tsw * 1 + ssw * 1 + wpad * 3
# Make the plot
fig = Figure(
    figsize=(fig_w, fig_h),
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
    "size": 8,
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


def plot_var(ts, t, m, xp, yp, label):
    ymin = min(min(t), min(m))
    ymax = max(max(t), max(m))
    ypad = (ymax - ymin) * 0.1
    if ypad == 0:
        ypad = 1
    ax_ts = fig.add_axes(
        [
            (wpad / fig_w) * (2 * xp - 1) + (tsw + ssw) * (xp - 1) / fig_w,
            (hpad / fig_h) * yp + (tsh / fig_h) * (yp - 1),
            tsw / fig_w,
            tsh / fig_h,
        ],
        xlim=(
            ts[0] - datetime.timedelta(days=15),
            ts[-1] + datetime.timedelta(days=15),
        ),
        ylim=(ymin - ypad, ymax + ypad),
    )
    ax_ts.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
    ax_ts.text(
        ts[0] - datetime.timedelta(days=15),
        ymax + ypad,
        label,
        ha="left",
        va="top",
        bbox=dict(boxstyle="square,pad=0.5", fc=(1, 1, 1, 1)),
        zorder=100,
    )
    ax_ts.add_line(Line2D(ts, t, linewidth=1, color=(0, 0, 0, 1), alpha=1.0, zorder=50))
    ax_ts.add_line(Line2D(ts, m, linewidth=1, color=(1, 0, 0, 1), alpha=1.0, zorder=60))
    ax_sc = fig.add_axes(
        [
            (wpad / fig_w) * (2 * xp) + (tsw * xp + ssw * (xp - 1)) / fig_w,
            (hpad / fig_h) * yp + (tsh / fig_h) * (yp - 1),
            ssw / fig_w,
            tsh / fig_h,
        ],
        xlim=(ymin - ypad, ymax + ypad),
        ylim=(ymin - ypad, ymax + ypad),
    )
    ax_sc.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
    ax_sc.scatter(t, m, s=1, color=(1, 0, 0, 1), zorder=60)
    ax_sc.add_line(
        Line2D(
            (ymin - ypad, ymax + ypad),
            (ymin - ypad, ymax + ypad),
            linewidth=1,
            color=(0, 0, 0, 1),
            alpha=0.2,
            zorder=10,
        )
    )


# Top - Raw
tsx = all_stats["dtp"]
ty = [x / 100 for x in all_stats["r_target"]]
my = [x / 100 for x in all_stats["r_model"]]
plot_var(tsx, ty, my, 1, 2, "Raw")


# Bottom - normalised
offset = 0
ty = [x - offset for x in all_stats["n_target"]]
my = [x - offset for x in all_stats["n_model"]]
plot_var(tsx, ty, my, 1, 1, "Normalised")


fig.savefig("multi.png")
