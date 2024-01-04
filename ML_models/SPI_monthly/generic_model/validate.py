#!/usr/bin/env python

# Plot a validation figure for the autoencoder.

# For all outputs:
#  1) Target field
#  2) Autoencoder output
#  3) scatter plot

import os
import sys
import numpy as np
import tensorflow as tf
import cmocean

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from specify import specification

# I don't need all the messages about a missing font (on Isambard)
import logging

logging.getLogger("matplotlib.font_manager").disabled = True

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--epoch", help="Epoch", type=int, required=False, default=250)
parser.add_argument("--year", help="Test year", type=int, required=False, default=None)
parser.add_argument(
    "--month", help="Test month", type=int, required=False, default=None
)
parser.add_argument(
    "--training",
    help="Use training data (not test)",
    default=False,
    action="store_true",
)
args = parser.parse_args()

from utilities import plots, grids

from ML_models.SPI_monthly.generic_model.makeDataset import getDataset
from ML_models.SPI_monthly.generic_model.autoencoderModel import DCVAE, getModel

purpose = "Test"
if args.training:
    purpose = "Train"
# Go through data and get the desired month
dataset = getDataset(specification, purpose=purpose).batch(1)
input = None
year = None
month = None
for batch in dataset:
    dateStr = tf.strings.split(batch[0][0][0], sep="/")[-1].numpy()
    year = int(dateStr[:4])
    month = int(dateStr[5:7])
    if (args.month is None or month == args.month) and (
        args.year is None or year == args.year
    ):
        input = batch
        break

if input is None:
    raise Exception("Month %04d-%02d not in %s dataset" % (year, month, purpose))

autoencoder = getModel(specification, args.epoch)

# Get autoencoded tensors
output = autoencoder.call(input, training=False)

nFields = specification["nOutputChannels"]

# Make the plot
figScale = 3.0
wRatios = (2, 2, 1.25)
fig = Figure(
    figsize=(figScale * sum(wRatios), figScale * nFields),
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
    "size": 12,
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


# Choose colourmap based on variable name
def get_cmap(name):
    if name == "PRATE" or name == "Precip":
        return cmocean.cm.tarn
    elif name == "MSLP":
        return cmocean.cm.diff
    else:
        return cmocean.cm.balance


# Each variable a row in it's own subfigure
subfigs = fig.subfigures(nFields, 1, wspace=0.01)

for varI in range(nFields):
    ax_var = subfigs[varI].subplots(nrows=1, ncols=3, width_ratios=wRatios)
    # Left - map of target
    varx = grids.E5sCube.copy()
    varx.data = np.squeeze(input[-1][:, :, :, varI].numpy())
    varx.data = np.ma.masked_where(varx.data == 0.0, varx.data, copy=False)
    if varI == 0:
        ax_var[0].set_title("%04d-%02d" % (year, month))
    ax_var[0].set_axis_off()
    x_img = plots.plotFieldAxes(
        ax_var[0],
        varx,
        vMax=1.25,
        vMin=-0.25,
        cMap=get_cmap(specification["outputNames"][varI]),
    )
    # Centre - map of model output
    vary = grids.E5sCube.copy()
    vary.data = np.squeeze(output[:, :, :, varI].numpy())
    vary.data = np.ma.masked_where(varx.data == 0.0, vary.data, copy=False)
    ax_var[1].set_axis_off()
    ax_var[1].set_title(specification["outputNames"][varI])
    x_img = plots.plotFieldAxes(
        ax_var[1],
        vary,
        vMax=1.25,
        vMin=-0.25,
        cMap=get_cmap(specification["outputNames"][varI]),
    )
    # Right - scatter plot of input::output
    ax_var[2].set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax_var[2].set_yticks([0, 0.25, 0.5, 0.75, 1])
    plots.plotScatterAxes(ax_var[2], varx, vary, vMin=-0.25, vMax=1.25, bins="log")


fig.savefig("comparison.png")
