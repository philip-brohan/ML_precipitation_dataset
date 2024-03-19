#!/usr/bin/env python

# Plot gamma fits to selected data points

import os
import sys
import iris
import iris.cube
import numpy as np
import argparse

from utilities import plots

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
with open("selected.pkl", "rb") as pkf:
    (random_points, raw) = pickle.load(pkf)


# Make the plot
fig = Figure(
    figsize=(15, 10),
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
    xmargin = 0.05
    ymargin = 0.03
    width = (1 - xmargin * 6) / 5
    height = (1 - ymargin * 6) / 5
    x_offset = xmargin + (width + xmargin) * x_i
    y_offset = ymargin + (height + ymargin) * y_i
    ax_sample = fig.add_axes([x_offset, y_offset, width, height])
    return ax_sample


for i in range(len(raw)):
    ax = make_axes(i)
    araw = raw[i]
    plots.plotHistAxes(ax, iris.cube.Cube(araw), bins=25)
    afit = araw
    shape, location, scale = gamma.fit(afit, method="MLE", floc=-0.0001)
    x = np.linspace(0, np.max(araw), num=100)
    y = gamma.pdf(x, shape, location, scale)
    ax.add_line(Line2D(x, y, color="red", linewidth=2))


fig.savefig("selected.png")