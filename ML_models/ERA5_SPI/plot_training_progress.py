#!/usr/bin/env python

# Plot time-series of training progress

import os
import sys
import math
import numpy as np
import tensorflow as tf

from tensorflow.core.util import event_pb2
from tensorflow.python.framework import tensor_util

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

from localise import ModelName

import argparse

# I don't need all the messages about a missing font
import logging

logging.getLogger("matplotlib.font_manager").disabled = True

parser = argparse.ArgumentParser()
parser.add_argument(
    "--comparator", help="Comparison model name", type=str, required=False, default=None
)
parser.add_argument(
    "--selfc", help="Compare with previous run", type=int, required=False, default=None
)
parser.add_argument(
    "--rscale",
    help="Scale RMS losses in comparator",
    type=float,
    required=False,
    default=1.0,
)
parser.add_argument(
    "--ymax", help="Y range maximum", type=float, required=False, default=None
)
parser.add_argument(
    "--ymin", help="Y range minimum", type=float, required=False, default=None
)
parser.add_argument(
    "--max_epoch", help="Max epoch to plot", type=int, required=False, default=None
)
args = parser.parse_args()


# Load the history
def loadHistory(LSC, offset=-1):
    history = {}
    summary_dir = "%s/MLP/%s/logs/Training" % (os.getenv("SCRATCH"), LSC)
    Rfiles = os.listdir(summary_dir)
    Rfiles.sort(key=lambda x: os.path.getmtime(os.path.join(summary_dir, x)))
    filename = Rfiles[offset]
    path = os.path.join(summary_dir, filename)
    serialized_records = tf.data.TFRecordDataset(path)
    for srecord in serialized_records:
        event = event_pb2.Event.FromString(srecord.numpy())
        for value in event.summary.value:
            t = tensor_util.MakeNdarray(value.tensor)
            if not value.tag in history.keys():
                history[value.tag] = []
            if len(history[value.tag]) < event.step + 1:
                history[value.tag].extend(
                    [0.0] * (event.step + 1 - len(history[value.tag]))
                )
            history[value.tag][event.step] = t.item()

    ymax = 0
    ymin = 1000000
    hts = {}
    n_epochs = len(history["Train_loss"])
    if args.max_epoch is not None:
        n_epochs = min(args.max_epoch, n_epochs)
    hts["epoch"] = list(range(n_epochs))[1:]
    for key in history:
        hts[key] = [abs(t) for t in history[key][1:n_epochs]]
    for key in ("Train_logpz", "Train_logqz_x", "Test_logpz", "Test_logqz_x"):
        ymax = max(ymax, max(hts[key]))
        ymin = min(ymin, min(hts[key]))

    return (hts, ymax, ymin, n_epochs)


(hts, ymax, ymin, epoch) = loadHistory(ModelName)

if args.selfc is not None:
    (chts, cymax, cymin, cepoch) = loadHistory(ModelName, args.selfc)
    epoch = max(epoch, cepoch)
    ymax = max(ymax, cymax)
    ymin = min(ymin, cymin)

if args.comparator is not None:
    (chts, cymax, cymin, cepoch) = loadHistory(args.comparator)
    epoch = max(epoch, cepoch)
    ymax = max(ymax, cymax)
    ymin = min(ymin, cymin)

if args.ymax is not None:
    ymax = args.ymax
if args.ymin is not None:
    ymin = args.ymin


fig = Figure(
    figsize=(15, 5),
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
    "size": 16,
}
matplotlib.rc("font", **font)
axb = fig.add_axes([0, 0, 1, 1])
axb.set_axis_off()
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


def addLine(ax, dta, key, col, z, rscale=1):
    ax.add_line(
        Line2D(
            dta["epoch"],
            np.array(dta[key]) * rscale,
            linewidth=2,
            color=col,
            alpha=1.0,
            zorder=z,
        )
    )


# Left - Main loss
ymaxL = max(100, max(hts["Train_RMSE"] + hts["Test_RMSE"]))
if args.comparator is not None or args.selfc is not None:
    ymaxL = max(ymaxL, max(chts["Train_RMSE"] + chts["Test_RMSE"]))
if args.ymax is not None:
    ymaxL = args.ymax
ax_prmsl = fig.add_axes(
    [0.055, 0.13, 0.27, 0.85], xlim=(-1, epoch + 1), ylim=(0, ymaxL)
)
ax_prmsl.set_ylabel("% Variance")
ax_prmsl.set_xlabel("epoch")
ax_prmsl.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)

addLine(ax_prmsl, hts, "Train_RMSE", (1, 0.5, 0.5, 1), 10)
addLine(ax_prmsl, hts, "Test_RMSE", (1, 0, 0, 1), 20)
if args.comparator is not None or args.selfc is not None:
    addLine(ax_prmsl, chts, "Train_RMSE", (0.5, 0.5, 1, 1), 10)
    addLine(ax_prmsl, chts, "Test_RMSE", (0, 0, 1, 1), 20)


# Centre - logpz
ax_lpz = fig.add_axes(
    [0.77 / 2, 0.13, 0.27, 0.85], xlim=(-1, epoch + 1), ylim=(ymin, ymax)
)
ax_lpz.set_ylabel("logpz")
ax_lpz.set_xlabel("epoch")
ax_lpz.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
addLine(ax_lpz, hts, "Train_logpz", (1, 0.5, 0.5, 1), 10)
addLine(ax_lpz, hts, "Test_logpz", (1, 0, 0, 1), 20)
if args.comparator is not None or args.selfc is not None:
    addLine(ax_lpz, chts, "Train_logpz", (0.5, 0.5, 1, 1), 10)
    addLine(ax_lpz, chts, "Test_logpz", (0, 0, 1, 1), 20)

# Right - logqz_x
ax_lqz = fig.add_axes(
    [0.715, 0.13, 0.27, 0.85], xlim=(-1, epoch + 1), ylim=(ymin, ymax)
)
ax_lqz.set_ylabel("logqz_x")
ax_lqz.set_xlabel("epoch")
ax_lqz.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
addLine(ax_lqz, hts, "Train_logqz_x", (1, 0.5, 0.5, 1), 10)
addLine(ax_lqz, hts, "Test_logqz_x", (1, 0, 0, 1), 20)
if args.comparator is not None or args.selfc is not None:
    addLine(ax_lqz, chts, "Train_logqz_x", (0.5, 0.5, 1, 1), 10)
    addLine(ax_lqz, chts, "Test_logqz_x", (0, 0, 1, 1), 20)


# Output as png
fig.savefig("training_progress.png")
