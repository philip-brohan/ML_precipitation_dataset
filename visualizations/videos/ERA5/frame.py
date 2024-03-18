#!/usr/bin/env python

# Make a month's worth of frames for a video of normalized values
# Use cubic interpolation to smooth between months.

import os
import sys
import datetime
import numpy as np
from scipy.interpolate import CubicSpline

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from utilities import plots, grids
import cmocean

from makeDataset import getDataset

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--year",
    type=int,
    required=True,
)
parser.add_argument(
    "--month",
    type=int,
    required=True,
)
parser.add_argument(
    "--intermediate",
    help="No of interpolated frames between months",
    type=int,
    required=False,
    default=6,
)
parser.add_argument("--variable", help="Variable", type=str, required=True)
args = parser.parse_args()

opdir = "%s/MLP/normalized_datasets/ERA5_tf_MM/videos/%s" % (
    os.getenv("SCRATCH"),
    args.variable,
)
if not os.path.isdir(opdir):
    os.makedirs(opdir)

# Colourmap
cmap = {
    "2m_temperature": cmocean.cm.balance,
    "mean_sea_level_pressure": cmocean.cm.diff,
    "total_precipitation": cmocean.cm.tarn,
}.get(args.variable)
if cmap is None:
    cmap = cmocean.cm.balance

# Get data for 5-month period centred on selected month
dts = []
ndata = None
startyear = args.year
if args.month < 3:
    startyear -= 1
endyear = args.year
if args.month > 10:
    endyear += 1
trainingData = getDataset(
    args.variable,
    startyear=startyear,
    endyear=endyear,
    cache=False,
    blur=None,
).batch(1)

tdts = datetime.datetime(args.year, args.month, 15, 0)
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    mdts = datetime.datetime(year, month, 15, 0)
    if abs((mdts - tdts).days) > 70:
        continue
    dts.append(mdts.timestamp())
    ndmo = batch[0][:, :, :, 0]
    if ndata is None:
        ndata = ndmo
    else:
        ndata = np.concatenate((ndata, ndmo), axis=0)

# Fit a cubic spline to each lat:lon point
interpolator = CubicSpline(dts, ndata, axis=0)

# At the month, and for args.intermediate points between the month and
#  the next month, plot the interpolated field.
ny = args.year
nm = args.month + 1
if nm > 12:
    ny += 1
    nm = 1
ndt = datetime.datetime(ny, nm, 15, 0)
dt_points = np.linspace(
    tdts.timestamp(), ndt.timestamp(), args.intermediate, endpoint=False
)
cbe = grids.E5sCube.copy()
for dtts in dt_points:
    ndata = interpolator(dtts)
    cbe.data = np.ma.MaskedArray(ndata,ndata==0)

    fig = Figure(
        figsize=(20, 10),
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
    ax_field = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    img = plots.plotFieldAxes(
        ax_field,
        cbe,
        cMap=cmap,
        vMin=-0.25,
        vMax=1.25,
    )
    dtm = datetime.date.fromtimestamp(dtts)
    # Label with the date
    ax_field.text(
        180 - 360 * 0.009,
        90 - 180 * 0.016,
        "%04d-%02d-%02d" % (dtm.year, dtm.month, dtm.day),
        horizontalalignment="right",
        verticalalignment="top",
        color="black",
        bbox=dict(
            facecolor=(0.6, 0.6, 0.6, 0.5), edgecolor="black", boxstyle="round", pad=0.5
        ),
        size=18,
        clip_on=True,
        zorder=500,
    )

    fig.savefig("%s/%04d-%02d-%02d.png" % (opdir, dtm.year, dtm.month, dtm.day))
