#!/usr/bin/env python

# Get the same field from all the normalized datasets and plot the comparison

import os
import numpy as np
import tensorflow as tf
from make_normalized_tensors.ERA5_tf_MM.tensor_utils import tensor_to_cube

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

# I don't need all the messages about a missing font (on Isambard)
import logging

logging.getLogger("matplotlib.font_manager").disabled = True

from utilities import plots

import cmocean

sDir = os.path.dirname(os.path.realpath(__file__))

rng = np.random.default_rng()

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--year",
    help="Year",
    type=int,
    required=True,
)
parser.add_argument("--month", help="Month", type=int, required=True)
args = parser.parse_args()


# Go through data and get the desired month
def get_month(dataset, year, month):
    for batch in dataset:
        dateStr = batch[1][0].numpy().decode("utf-8")
        y = int(dateStr[:4])
        m = int(dateStr[5:7])
        if y == year and m == month:
            return tensor_to_cube(tf.squeeze(batch[0]))
    raise Exception("Month %04d-%02d not in dataset" % (year, month))


# Go through the raw sources and get the desired month from each
rawMonths = {}
# ERA5
import visualizations.stripes.ERA5.makeDataset

rawDS = visualizations.stripes.ERA5.makeDataset.getDataset(
    "total_precipitation",
    startyear=1950,
    endyear=2023,
    cache=False,
    blur=None,
).batch(1)
rawMonths["ERA5"] = get_month(rawDS, args.year, args.month)
# TWCR
import visualizations.stripes.TWCR.makeDataset

rawDS = visualizations.stripes.TWCR.makeDataset.getDataset(
    "PRATE",
    startyear=1850,
    endyear=2023,
    cache=False,
    blur=None,
).batch(1)
rawMonths["TWCR"] = get_month(rawDS, args.year, args.month)
# CRU
import visualizations.stripes.CRU.makeDataset

rawDS = visualizations.stripes.CRU.makeDataset.getDataset(
    startyear=1850,
    endyear=2023,
    cache=False,
    blur=None,
).batch(1)
rawMonths["CRU"] = get_month(rawDS, args.year, args.month)
# GPCC_in-situ
import visualizations.stripes.GPCC.in_situ.makeDataset

rawDS = visualizations.stripes.GPCC.in_situ.makeDataset.getDataset(
    startyear=1850,
    endyear=2023,
    cache=False,
    blur=None,
).batch(1)
rawMonths["GPCC_in-situ"] = get_month(rawDS, args.year, args.month)
# GPCP
import visualizations.stripes.GPCP.makeDataset

rawDS = visualizations.stripes.GPCP.makeDataset.getDataset(
    startyear=1850,
    endyear=2023,
    cache=False,
    blur=None,
).batch(1)
rawMonths["GPCP"] = get_month(rawDS, args.year, args.month)

# Get global min and max values
gMin = -0.25
gMax = 1.25

# Plot the set of normalized tensors
fig = Figure(
    figsize=(40, 30),
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
ax_var = fig.subplots(nrows=3, ncols=2)
ax_var = ax_var.flatten()
for i, k in enumerate(rawMonths.keys()):
    ax = ax_var[i]
    plots.plotFieldAxes(
        ax,
        rawMonths[k],
        vMin=gMin,
        vMax=gMax,
        cMap=cmocean.cm.balance,
    )
    ax.set_title(k)

ax_var[5].axis("off")

fig.savefig("normalized_precip.png")
