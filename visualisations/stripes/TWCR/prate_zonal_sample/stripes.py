#!/usr/bin/env python

# 20CRv3 stripes - normalised temperatures.
# Monthly, resolved in latitude, averaging in longitude,
#  single ensemble member.

import os
import sys
import numpy
import datetime
import numpy as np
import tensorflow as tf
from scipy.stats import uniform, norm

rng = np.random.default_rng()

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

start = datetime.datetime(1850, 1, 1, 0, 0)
end = datetime.datetime(2023, 12, 31, 23)

sys.path.append("%s/.." % os.path.dirname(__file__))
from makeDataset import getDataset

# Go through data and extract zonal mean for each month
dts = []
ndata = None
trainingData = getDataset(
    "PRATE",
    startyear=start.year,
    endyear=end.year,
    cache=False,
    blur=None,
).batch(1)

for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    dts.append(datetime.datetime(year, month, 15, 0))
    nd2d = tf.squeeze(batch[0])
    nd2dt = tf.transpose(nd2d)
    ndmo = tf.transpose(tf.random.shuffle(nd2dt)[0, :])
    ndmo = tf.transpose(ndmo).numpy()
    ndmo = np.reshape(ndmo, [721, 1])
    if ndata is None:
        ndata = ndmo
    else:
        ndata = np.concatenate((ndata, ndmo), axis=1)


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

# Map normally distributed ndata to a uniform distribution for plotting
#  (means plot has ~same amount of each colour).
# cdf = norm.cdf(ndata, loc=0.5, scale=0.2)
# ndata = uniform.ppf(cdf, loc=0, scale=1)
s = ndata.shape
y = numpy.linspace(0, 1, s[0] + 1)
x = [(a - datetime.timedelta(days=15)).timestamp() for a in dts]
x.append((dts[-1] + datetime.timedelta(days=15)).timestamp())
img = ax.pcolorfast(x, y, ndata, cmap="RdYlBu_r", alpha=1.0, vmin=0, vmax=1, zorder=100)


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
        size=14,
        clip_on=True,
        zorder=200,
    )


for year in range(1860, 2020, 10):
    add_dateline(axg, year)

# ColourBar
ticv = [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
ticl = ["%3.2f" % x for x in ticv]
cdf = uniform.cdf(ticv, loc=0, scale=1)
tics = norm.ppf(cdf, loc=0.5, scale=0.2)
ax_cb = fig.add_axes([0.925, 0.06125, 0.05, 0.9])
ax_cb.set_axis_off()
cb = fig.colorbar(
    img,
    ax=ax_cb,
    location="right",
    orientation="vertical",
    fraction=1.0,
    ticks=tics,
    format=matplotlib.ticker.FixedFormatter(ticl),
    label="Quantile",
)


fig.savefig("PRATE.png")
