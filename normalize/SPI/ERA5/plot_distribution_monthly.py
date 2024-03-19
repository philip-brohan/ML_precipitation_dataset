#!/usr/bin/env python

# Plot raw and normalized precipitation for a selected month
# Map and distribution.

import os
import sys
import numpy as np

from utilities import plots
from get_data import load_monthly

from normalize import load_fitted, normalize_cube

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean
import argparse

from scipy.stats import gamma

parser = argparse.ArgumentParser()
parser.add_argument(
    "--year", help="Year to plot", type=int, required=False, default=1969
)
parser.add_argument(
    "--month", help="Month to plot", type=int, required=False, default=3
)
args = parser.parse_args()

# Load the fitted values
(shape, location, scale) = load_fitted()

# Load the precip for the selected month
raw = load_monthly.load(organisation="ERA5", year=args.year, month=args.month)

# Make the normalized version
normalized = normalize_cube(raw, shape, location, scale)

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


ax_raw = fig.add_axes([0.02, 0.515, 0.607, 0.455])
plots.plotFieldAxes(
    ax_raw,
    raw,
    plotCube=plots.plot_cube(),
    vMin=0,
    vMax=np.percentile(raw.data.data, 95),
    cMap=cmocean.cm.rain,
)

ax_hist_raw = fig.add_axes([0.683, 0.535, 0.303, 0.435])
plots.plotHistAxes(ax_hist_raw, raw, bins=25)

ax_normalized = fig.add_axes([0.02, 0.03, 0.607, 0.455])
plots.plotFieldAxes(
    ax_normalized,
    normalized,
    plotCube=plots.plot_cube(),
    vMin=-0.25,
    vMax=1.25,
    # vMin=np.percentile(normalized.data.data, 5),
    # vMax=np.percentile(normalized.data.data, 95),
    cMap=cmocean.cm.rain,
)

ax_hist_normalized = fig.add_axes([0.683, 0.05, 0.303, 0.435])
plots.plotHistAxes(ax_hist_normalized, normalized, vMin=-0.25, vMax=1.25, bins=25)


fig.savefig("monthly.png")