#!/usr/bin/env python

from importlib.metadata import files
import os
import argparse
import pickle
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable
from astropy.convolution import convolve

parser = argparse.ArgumentParser()
parser.add_argument(
    "--label",  # name for this validation run
    type=str,
    required=True,
)
parser.add_argument(
    "--target",
    type=str,
    required=True,
)
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
args = parser.parse_args()


# Convolution smoothing
def csmooth(nmonths, ndata):
    if nmonths < 0:  # Want residual from smoothing
        n2 = csmooth(nmonths * -1, ndata)
        return ndata - n2 + 0.5
    if nmonths == 1:
        return ndata
    else:
        filter = np.full((nmonths), 1 / nmonths)
        return convolve(ndata, filter, boundary="extend", preserve_nan=True)


# Load the model data
sDir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")
with open(
    "%s/%s/series/%s_%s_%s.pkl"
    % (sDir, args.label, args.mask_file, args.rchoice, "adjusted"),
    "rb",
) as dfile:
    model_ndata = pickle.load(dfile)

# Load the target data
with open(
    "%s/sources/%s/%s_%s_%s.pkl"
    % (sDir, args.target, args.mask_file, args.rchoice, args.target),
    "rb",
) as dfile:
    target_ndata = pickle.load(dfile)

# Reformat data into three lists: date, pred, targ
pred_list = []
targ_list = []
date_list = []
dlist = sorted(
    list(dict.fromkeys(list(model_ndata.keys()) + list(target_ndata.keys())))
)  # unique dates in order
for i in range(len(dlist)):
    date_list.append(datetime.strptime(dlist[i][:6], "%Y%m"))  # convert to datetime
    if dlist[i] in model_ndata:
        pred_list.append(model_ndata[dlist[i]])  # pred
    else:
        pred_list.append(np.nan)  # pred missing
    if dlist[i] in target_ndata:
        targ_list.append(target_ndata[dlist[i]])  # targ
    else:
        targ_list.append(np.nan)  # targ missing

dates = date_list
prediction_ts = csmooth(args.nmonths, np.asarray(pred_list))
target_ts = csmooth(args.nmonths, np.asarray(targ_list))

if len(dates) == 0 or prediction_ts.size == 0 or target_ts.size == 0:
    raise SystemExit("No data loaded from pickle(s)")


# Create a 2x2 layout: left column two stacked timeseries (top: pred+target, bottom: difference),
# right column single axis spanning both rows for the scatter
fig = plt.figure(figsize=(14, 6))
gs = fig.add_gridspec(
    2, 2, width_ratios=(3, 1), height_ratios=(1, 1), wspace=0.18, hspace=0.18
)

# Top-left: time series (prediction + target)
ax_ts = fig.add_subplot(gs[0, 0])
ax_ts.plot(dates, prediction_ts, label="Adjusted", lw=1)
ax_ts.plot(dates, target_ts, label="Original", lw=1)
ax_ts.set_ylabel("Value")
ax_ts.set_title(os.path.basename(args.label))
ax_ts.legend(loc="upper left")
ax_ts.xaxis.set_major_locator(mdates.YearLocator(5))
ax_ts.xaxis.set_minor_locator(mdates.YearLocator(1))
ax_ts.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.setp(ax_ts.get_xticklabels(), visible=False)  # hide top x labels (use bottom axis)

# Bottom-left: difference time series (target - prediction)
ax_diff = fig.add_subplot(gs[1, 0], sharex=ax_ts)
diff_ts = target_ts - prediction_ts
ax_diff.plot(dates, diff_ts, label="Original - Adjusted", color="C2", lw=1)
ax_diff.axhline(0.0, color="k", linestyle="--", linewidth=0.6)
ax_diff.set_ylabel("Original - Adjusted")
ax_diff.set_xlabel("Time")
ax_diff.xaxis.set_major_locator(mdates.YearLocator(5))
ax_diff.xaxis.set_minor_locator(mdates.YearLocator(1))
ax_diff.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.setp(ax_diff.get_xticklabels(), rotation=45, ha="right")

# Right: prediction vs target scatter spanning both rows
# use hexbin for density plotting instead of scatter
ax_sc = fig.add_subplot(gs[:, 1])
hb = ax_sc.hexbin(target_ts, prediction_ts, gridsize=60, cmap="viridis", bins="log")
# 1:1 line
mn = float(np.nanmin(np.stack((target_ts, prediction_ts))))
mx = float(np.nanmax(np.stack((target_ts, prediction_ts))))
ax_sc.plot([mn, mx], [mn, mx], "k--", linewidth=0.8)
ax_sc.set_xlabel("Original")
ax_sc.set_ylabel("Adjusted")
ax_sc.set_title("Adjusted vs Original")
ax_sc.set_aspect("equal", adjustable="box")
# create a colorbar whose height matches the hexbin axis
divider = make_axes_locatable(ax_sc)
cax = divider.append_axes("right", size="5%", pad=0.06)
# cb = fig.colorbar(hb, cax=cax, label="log10(count)")

# correlation coefficient (ignore NaNs)
mask = (~np.isnan(target_ts)) & (~np.isnan(prediction_ts))
if mask.sum() >= 2:
    corr = np.corrcoef(target_ts[mask], prediction_ts[mask])[0, 1]
else:
    corr = float("nan")
# display in corner with a light background
ax_sc.text(
    0.05,
    0.95,
    f"r = {corr:.3f}",
    transform=ax_sc.transAxes,
    va="top",
    ha="left",
    fontsize=10,
    bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"),
)

plt.tight_layout()

if args.mask_file is None:
    args.mask_file = "None"
if args.rchoice is None:
    args.rchoice = "None"
ns = ""
sDir += "/%s/series" % args.label
if not os.path.isdir(sDir):
    os.makedirs(sDir)

fig.savefig(
    "%s/%s%s_%s_%03d_adjusted.webp"
    % (sDir, ns, args.mask_file, args.rchoice, args.nmonths),
    dpi=150,
    bbox_inches="tight",
)
