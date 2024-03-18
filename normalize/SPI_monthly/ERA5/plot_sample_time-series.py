#!/usr/bin/env python

# Plot time-series of the sample data points (raw and normalized)

import os
import sys
import iris
import iris.cube
import numpy as np
import argparse

from normalize import match_normal

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

import cmocean
import pickle

from scipy.stats import gamma

parser = argparse.ArgumentParser()
parser.add_argument(
    "--month", help="Month to extract", type=int, required=False, default=3
)
args = parser.parse_args()

# Retrieve the sample data
with open("sample_m%02d.pkl" % args.month, "rb") as pkf:
    (random_points, raw) = pickle.load(pkf)


# Make the plot
fig = Figure(
    figsize=(30, 10),
    dpi=200,
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


# Make an axes for each sample
def make_axes(sample_i):
    x_i = sample_i % 5
    y_i = sample_i // 5
    xmargin = 0.03
    ymargin = 0.03
    width = (1 - xmargin * 6) / 5
    height = (1 - ymargin * 6) / 5
    x_offset = xmargin + (width + xmargin) * x_i
    y_offset = ymargin + (height + ymargin) * y_i
    ax_sample = fig.add_axes([x_offset, y_offset, width, height])
    return ax_sample


for i in range(25):
    ax = make_axes(i)
    araw = raw[i]
    afit = araw
    shape, location, scale = gamma.fit(afit, method="MLE", floc=-0.0001)
    araw = araw  # Only centre point, no surroundings
    x = list(range(len(araw)))
    ax.set_xlim(0, len(araw))
    ax.set_ylim(0, 0.25**3)
    ax.add_line(Line2D(x, araw, color="blue", linewidth=2))
    ax2 = ax.twinx()
    norm = match_normal(raw[i], (shape, location, scale))
    ax2.set_xlim(0, len(araw))
    ax2.set_ylim(-0.25, 1.25)
    ax2.add_line(Line2D(x, norm, color="red", linewidth=2))


fig.savefig("sample_time-series_m%02d.png" % args.month)
