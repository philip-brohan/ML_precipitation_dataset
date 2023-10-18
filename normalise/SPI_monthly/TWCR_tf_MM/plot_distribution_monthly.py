#!/usr/bin/env python

# Plot raw and normalised precipitation for a selected month
# Map and distribution.

import os
import sys
import numpy as np

from utilities import plots, grids
from get_data.TWCR import TWCR_monthly_load

from normalise import load_fitted, normalise_cube

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
parser.add_argument(
    "--variable",
    help="Name of variable to use (PRATE, TMP2m, PRMSL, ...)",
    type=str,
    default="PRATE",
)
parser.add_argument(
    "--member",
    help="Ensemble member to use. (Default, sample randomly)",
    type=int,
    default=1,
)
args = parser.parse_args()

# Load the fitted values
(shape, location, scale) = load_fitted(args.month, variable=args.variable)

# Load the raw data for the selected month
raw = TWCR_monthly_load.load_monthly_member(
    variable=args.variable,
    year=args.year,
    month=args.month,
    member=args.member,
    grid=grids.E5sCube,
)

# Make the normalised version
normalised = normalise_cube(raw, shape, location, scale)

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

# choose actual and normalised data colour maps based on variable
cmaps = (cmocean.cm.balance, cmocean.cm.balance)
if args.variable == "PRATE":
    cmaps = (cmocean.cm.rain, cmocean.cm.tarn)
if args.variable == "PRMSL":
    cmaps = (cmocean.cm.diff, cmocean.cm.diff)


ax_raw = fig.add_axes([0.02, 0.515, 0.607, 0.455])
plots.plotFieldAxes(
    ax_raw,
    raw,
    plotCube=grids.E5sCube,
    vMin=0 if args.variable == "PRATE" else np.percentile(raw.data.data, 5),
    vMax=np.percentile(raw.data.data, 95),
    cMap=cmaps[0],
)

ax_hist_raw = fig.add_axes([0.683, 0.535, 0.303, 0.435])
plots.plotHistAxes(ax_hist_raw, raw, bins=25)

ax_normalised = fig.add_axes([0.02, 0.03, 0.607, 0.455])
plots.plotFieldAxes(
    ax_normalised,
    normalised,
    plotCube=grids.E5sCube,
    vMin=-0.25,
    vMax=1.25,
    # vMin=np.percentile(normalised.data.data, 5),
    # vMax=np.percentile(normalised.data.data, 95),
    cMap=cmaps[1],
)

ax_hist_normalised = fig.add_axes([0.683, 0.05, 0.303, 0.435])
plots.plotHistAxes(ax_hist_normalised, normalised, vMin=-0.25, vMax=1.25, bins=25)


fig.savefig("monthly.png")