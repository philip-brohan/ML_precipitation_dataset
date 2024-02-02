#!/usr/bin/env python

# Plot normalised time-series

import os
import datetime
import pickle
import numpy as np
from astropy.convolution import convolve

sDir = os.path.dirname(os.path.realpath(__file__))

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# I don't need all the messages about a missing font
import logging

logging.getLogger("matplotlib.font_manager").disabled = True
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--start_year",
    type=int,
    required=False,
    default=1850,
)
parser.add_argument(
    "--end_year",
    type=int,
    required=False,
    default=2023,
)
parser.add_argument(
    "--nmonths",
    help="Length of convolution filter",
    type=int,
    required=False,
    default=1,
)
parser.add_argument(
    "--ymin",
    type=float,
    required=False,
    default=250,
)
parser.add_argument(
    "--ymax",
    type=float,
    required=False,
    default=300,
)
parser.add_argument(
    "--linewidth",
    type=float,
    required=False,
    default=1,
)
args = parser.parse_args()


start = datetime.date(args.start_year, 1, 15)
end = datetime.date(args.end_year, 12, 15)


# Make the plot
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
    "size": 18,
}
matplotlib.rc("font", **font)

# List of datasets to plot (and colour to use)
datasets = {
    "ERA5_t2m": (1, 0, 0, 1),
    "ERA5_sst": (0, 0, 1, 1),
    "TWCR_t2m": (0.5, 0, 0, 1),
    "TWCR_sst": (0, 0, 0.5, 1),
    # "HadISST": (0, 0.5, 0.5, 1),
    "HadCRUT": (0, 0, 0, 0.1),
}

# Background
axb = fig.add_axes([-0.01, -0.01, 1.02, 1.02])
axb.add_patch(
    Rectangle(
        (0, 0),
        1,
        1,
        facecolor=(1, 1, 1, 1),
        fill=True,
        zorder=1,
    )
)

# Data axes
ax_ts = fig.add_axes(
    [0.05, 0.1, 0.9, 0.75],
    xlim=(start, end),
    ylim=(args.ymin, args.ymax),
)
ax_ts.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)


def plot_var(ndata, width, col, label):
    ts = {}
    t = {}
    for dk in sorted(ndata.keys()):
        # if np.isnan(ndata[dk]):
        #    continue
        year = int(dk[:4])
        month = int(dk[4:6])
        if year < args.start_year or year > args.end_year:
            continue
        member = dk[6:]
        if member not in ts.keys():
            ts[member] = []
            t[member] = []
        ts[member].append(datetime.date(year, month, 15))
        t[member].append(ndata[dk])
    for member in ts.keys():
        tp = csmooth(args.nmonths, t[member])
        ax_ts.add_line(
            Line2D(
                ts[member],
                tp,
                linewidth=width,
                color=col,
                zorder=50,
                label=label,
            )
        )
        label = None  # Only label once per dataset


def csmooth(nmonths, ndata):
    if nmonths < 0:  # Want residual from smoothing
        n2 = csmooth(nmonths * -1, ndata)
        return ndata - n2 + 0.5
    if nmonths == 1:
        return ndata
    else:
        filter = np.full((nmonths), 1 / nmonths)
        return convolve(ndata, filter, boundary="extend", preserve_nan=True)


for ds in datasets.keys():
    try:
        with open("%s.pkl" % ds, "rb") as dfile:
            ndata = pickle.load(dfile)
    except Exception:
        continue
    plot_var(ndata, args.linewidth, col=datasets[ds], label=ds)

handles, labels = ax_ts.get_legend_handles_labels()
ax_ts.legend(handles, labels, loc="upper left")

fig.savefig("%s/temperatures_%03d.png" % (sDir, args.nmonths))
