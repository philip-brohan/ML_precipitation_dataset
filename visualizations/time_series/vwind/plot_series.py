#!/usr/bin/env python

# Plot normalized time-series

import os
import datetime
import pickle
import numpy as np
from astropy.convolution import convolve

sDir = "%s/visualizations/time_series/vwind" % os.getenv("PDIR")

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
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
    default=0.425,
)
parser.add_argument(
    "--ymax",
    type=float,
    required=False,
    default=0.575,
)
parser.add_argument(
    "--linewidth",
    type=float,
    required=False,
    default=1.0,
)
parser.add_argument(
    "--rchoice",
    help="Area reduction choice (None or 'area')",
    type=str,
    required=False,
    default="None",
)
parser.add_argument(
    "--mask_file",
    help="File containing averaging data mask",
    type=str,
    required=False,
    default="None",
)
parser.add_argument(
    "--nosat",
    help="Don't plot satellite based datasets",
    action="store_true",
)
parser.add_argument(
    "--nomodel",
    help="Don't plot model datasets",
    action="store_true",
)
parser.add_argument(
    "--spectrum",
    help="Plot frequency spectrum (power) instead of time series",
    action="store_true",
)
parser.add_argument(
    "--max_frequency",
    help="Max frequency to show in spectrum plots (in 1/years)",
    type=float,
    required=False,
    default=1.0,
)


args = parser.parse_args()


start = datetime.date(args.start_year, 1, 15)
end = datetime.date(args.end_year, 12, 15)


# Make the plot
if args.spectrum:
    figsize = (10, 10)
else:
    figsize = (20, 10)
fig = Figure(
    figsize=figsize,
    dpi=100,
    facecolor=(1, 1, 1, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=True,
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
    "ERA5": (0, 0, 1, 1),
    "TWCR": (0, 0, 0.5, 1),
}
if not args.nomodel:
    datasets["GC5"] = (1, 0.5, 0.5, 1)

# Data axes
if args.spectrum:
    # frequency axis in cycles per year (monthly sampling -> Nyquist = 6 cyc/yr)
    ax_ts = fig.add_axes([0.1, 0.1, 0.85, 0.85], xlim=(0.0, args.max_frequency))
    ax_ts.set_xlabel("Frequency (cycles/year)")
    ax_ts.set_ylabel("Power")
    ax_ts.set_yscale("log")
else:
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
        if args.spectrum:
            y = np.asarray(t[member], dtype=float)
            # handle NaNs: replace with mean so FFT works
            if np.isnan(y).any():
                y = np.nan_to_num(y, nan=np.nanmean(y))
            # remove mean
            y = y - np.mean(y)
            N = y.size
            if N < 2:
                continue
            # real FFT, sampling interval d = 1 month -> sampling rate = 12 samples/year
            yf = np.fft.rfft(y)
            psd = (np.abs(yf) ** 2) / N
            freqs = np.fft.rfftfreq(N, d=1.0 / 12.0)  # cycles per year
            # skip the zero-frequency term for plotting if desired
            psd = csmooth(args.nmonths, psd[1:])
            ax_ts.plot(
                freqs[1:], psd, linewidth=width, color=col, zorder=50, label=label
            )
            ax_ts.set_xscale("linear")
            label = None
        else:
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
        with open(
            "%s/%s_%s_%s.pkl" % (sDir, args.mask_file, args.rchoice, ds), "rb"
        ) as dfile:
            ndata = pickle.load(dfile)
    except Exception:
        continue
    plot_var(ndata, args.linewidth, col=datasets[ds], label=ds)

handles, labels = ax_ts.get_legend_handles_labels()
if args.spectrum:
    ax_ts.legend(handles, labels, loc="upper right", ncol=3)
else:
    ax_ts.legend(handles, labels, loc="upper left", ncol=6)

ns = ""
if args.nosat:
    ns = "ns_"
if args.spectrum:
    ns = "spectrum_%s" % ns
fig.savefig(
    "%s/%s%s_%s_vwind_%03d.webp"
    % (sDir, ns, args.mask_file, args.rchoice, args.nmonths)
)
