#!/usr/bin/env python

# GPCC in-situ stripes - normalized values.
# Monthly, resolved in latitude,

import os
import sys
import numpy
import datetime
import re
import numpy as np
import tensorflow as tf
from astropy.convolution import convolve

sDir = os.path.dirname(os.path.realpath(__file__))

rng = np.random.default_rng()

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import cmocean

from makeDataset import getDataset

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--reduce",
    help="Longitude reduction method",
    type=str,
    required=False,
    default="sample",
)
parser.add_argument(
    "--convolve", help="Convolution filter", type=str, required=False, default="none"
)
parser.add_argument(
    "--vmin",
    type=float,
    required=False,
    default=0.0,
)
parser.add_argument(
    "--vmax",
    type=float,
    required=False,
    default=1.0,
)
parser.add_argument(
    "--startyear",
    type=int,
    required=False,
    default=1891,
)
parser.add_argument(
    "--endyear",
    type=int,
    required=False,
    default=2023,
)
args = parser.parse_args()

start = datetime.datetime(args.startyear, 1, 1, 0, 0)
end = datetime.datetime(args.endyear, 12, 31, 23)


# Longitude reduction
def longitude_reduce(choice, ndata):
    result = np.zeros([721, 1])
    if choice == "sample":
        nd2d = tf.squeeze(ndata).numpy()
        for i in range(nd2d.shape[0]):  # Iterate over latitudes
            alat = nd2d[i, :][nd2d[i, :] != 0]
            if len(alat) > 0:
                result[i, 0] = rng.choice(alat, size=1)
        return result
    if choice == "mean":
        nd2d = tf.squeeze(ndata).numpy()
        for i in range(nd2d.shape[0]):  # Iterate over latitudes
            alat = nd2d[i, :][nd2d[i, :] != 0]
            if len(alat) > 0:
                result[i, 0] = np.mean(alat)
        return result
    raise Exception("Unsupported reduction choice %s" % choice)


# Convolution smoothing
def csmooth(choice, ndata):
    ndata[ndata == 0] = np.nan
    if choice[:3] == "sub":  # Want residual from smoothing
        n2 = csmooth(choice[4:], ndata)
        return ndata - n2 + 0.5
    if choice == "none":
        return ndata
    if choice == "annual":
        filter = np.full((1, 13), 1 / 13)
        return convolve(ndata, filter, boundary="extend")
    result = re.search(r"(\d+)x(\d+)", choice)
    if result is not None:
        hv = int(result.groups()[0])
        vv = int(result.groups()[1])
        filter = np.full((vv, hv), 1 / (vv * hv))
        return convolve(ndata, filter, boundary="extend")
    raise Exception("Unsupported convolution choice %s" % choice)


# Colourmap
cmap = cmocean.cm.tarn

# Go through data and extract zonal mean for each month
dts = []
ndata = None
trainingData = getDataset(
    startyear=start.year,
    endyear=end.year,
    cache=False,
    blur=None,
).batch(1)

for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    dts.append(datetime.datetime(year, month, 15, 0))
    ndmo = longitude_reduce(args.reduce, batch[0])
    if ndata is None:
        ndata = ndmo
    else:
        ndata = np.concatenate((ndata, ndmo), axis=1)

ndata = np.ma.MaskedArray(ndata, ndata == 0.0)
omask = ndata.mask.copy()
# Filter
ndata = csmooth(args.convolve, ndata)
ndata = np.ma.MaskedArray(ndata, np.isnan(ndata))
ndata = np.ma.MaskedArray(ndata, omask)

# Plot the resulting array as a 2d colourmap
fig = Figure(
    figsize=(16, 4.5),  # Width, Height (inches)
    dpi=300,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
    subplotpars=None,
    tight_layout=None,
)
font = {"size": 12}
matplotlib.rc("font", **font)
canvas = FigureCanvas(fig)
matplotlib.rc("image", aspect="auto")

# White background for whole figure
axb = fig.add_axes(
    [0.0, 0.0, 1.0, 1.0],
    facecolor="white",
    xmargin=0,
    ymargin=0,
)
axb.set_axis_off()
axb.fill([0, 1, 1, 0], [0, 0, 1, 1], "white")

# Add a textured grey background
s = (2000, 600)
ax2 = fig.add_axes([0.0, 0.05, 0.9, 0.95], facecolor="green")
ax2.set_axis_off()
nd2 = np.random.rand(s[1], s[0])
clrs = []
for shade in np.linspace(0.42 + 0.01, 0.36 + 0.01):
    clrs.append((shade, shade, shade, 1))
y = np.linspace(0, 1, s[1])
x = np.linspace(0, 1, s[0])
img = ax2.pcolormesh(
    x,
    y,
    nd2,
    cmap=matplotlib.colors.ListedColormap(clrs),
    alpha=1.0,
    shading="gouraud",
    zorder=10,
)

# Plot the stripes
ax = fig.add_axes(
    [0.0, 0.05, 0.9, 0.95],
    facecolor="black",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(1, 0),
)
ax.set_axis_off()

s = ndata.shape
y = 1.0 - numpy.linspace(0, 1, s[0] + 1)
x = [(a - datetime.timedelta(days=15)).timestamp() for a in dts]
x.append((dts[-1] + datetime.timedelta(days=15)).timestamp())
img = ax.pcolorfast(
    x, y, ndata, cmap=cmap, alpha=1.0, vmin=args.vmin, vmax=args.vmax, zorder=100
)

# Add a latitude grid
axg = fig.add_axes(
    [0.0, 0.05, 0.9, 0.95],
    facecolor="green",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(0, 1),
)
axg.set_axis_off()


def add_latline(ax, latitude):
    latl = (latitude + 90) / 180
    ax.add_line(
        Line2D(
            [start.timestamp(), end.timestamp()],
            [latl, latl],
            linewidth=0.75,
            color=(0.2, 0.2, 0.2, 1),
            zorder=200,
        )
    )


for lat in (-60, -30, 0, 30, 60):
    add_latline(axg, lat)

# Add a date grid
axg = fig.add_axes(
    [0.0, 0, 0.9, 1],
    facecolor="green",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(0, 1),
)
axg.set_axis_off()


def add_dateline(ax, year):
    x = datetime.datetime(year, 1, 1, 0, 0).timestamp()
    ax.add_line(
        Line2D(
            [x, x], [0.04, 1.0], linewidth=0.75, color=(0.2, 0.2, 0.2, 1), zorder=200
        )
    )
    ax.text(
        x,
        0.024,
        "%04d" % year,
        horizontalalignment="center",
        verticalalignment="center",
        color="black",
        clip_on=True,
        zorder=200,
    )


for year in range((args.startyear // 10) * 10, args.endyear, 10):
    if year == args.startyear or year == args.endyear:
        continue
    add_dateline(axg, year)

# ColourBar
ax_cb = fig.add_axes([0.925, 0.06125, 0.05, 0.9])
ax_cb.set_axis_off()
cb = fig.colorbar(
    img,
    ax=ax_cb,
    location="right",
    orientation="vertical",
    fraction=1.0,
    label="Quantile",
)


fig.savefig("%s/in_situ_%s_%s.png" % (sDir, args.reduce, args.convolve))
