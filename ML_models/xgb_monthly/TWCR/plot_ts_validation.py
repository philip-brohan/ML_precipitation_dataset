#!/usr/bin/env python

import os
import argparse
import glob
import pickle
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

parser = argparse.ArgumentParser(description="Plot time-series from validate_time_series pickles")
parser.add_argument(
    "--pkl",
    help="Path to a single pickle, a directory containing .pkl files, or a glob pattern (one file per year)",
    required=True,
)
parser.add_argument(
    "--out",
    help="Output filename",
    required=True,
)
args = parser.parse_args()

# accept single file, directory of .pkl, or a glob pattern
if os.path.isdir(args.pkl):
    files = sorted(glob.glob(os.path.join(args.pkl, "*.pkl")))
elif any(ch in args.pkl for ch in ("*", "?")):
    files = sorted(glob.glob(args.pkl))
else:
    files = [args.pkl]

if not files:
    raise SystemExit(f"No pickle files found for {args.pkl!s}")

# load and concatenate data from all files (expect each file to contain date_ts, prediction_ts, target_ts)
date_list = []
pred_list = []
targ_list = []
for pfile in files:
    with open(pfile, "rb") as f:
        data = pickle.load(f)
    if isinstance(data, dict):
        ds = data.get("date_ts")
        ps = data.get("prediction_ts")
        ts = data.get("target_ts")
    else:
        ds, ps, ts = data
    if ds is None or ps is None or ts is None:
        raise SystemExit(f"Pickle {pfile} missing expected keys")
    # extend lists (accept list/array)
    date_list.extend(list(ds))
    pred_list.extend(list(np.asarray(ps)))
    targ_list.extend(list(np.asarray(ts)))

date_ts = date_list
prediction_ts = np.asarray(pred_list)
target_ts = np.asarray(targ_list)

if len(date_ts) == 0 or prediction_ts.size == 0 or target_ts.size == 0:
    raise SystemExit("No data loaded from pickle(s)")

# convert date strings "YYYY-MM" (or similar) to datetimes if needed
dates = []
for d in date_ts:
    if isinstance(d, str):
        # try common formats
        try:
            dates.append(datetime.strptime(d, "%Y-%m"))
        except ValueError:
            try:
                dates.append(datetime.strptime(d, "%Y-%m-%d"))
            except ValueError:
                # last resort: parse year-only or isoformat
                dates.append(datetime.fromisoformat(d))
    elif isinstance(d, (int, float)):
        # year integer
        dates.append(datetime(int(d), 1, 1))
    else:
        dates.append(d)

# Create a 2x2 layout: left column two stacked timeseries (top: pred+target, bottom: difference),
# right column single axis spanning both rows for the scatter
fig = plt.figure(figsize=(14, 6))
gs = fig.add_gridspec(2, 2, width_ratios=(3, 1), height_ratios=(1, 1), wspace=0.18, hspace=0.18)

# Top-left: time series (prediction + target)
ax_ts = fig.add_subplot(gs[0, 0])
ax_ts.plot(dates, prediction_ts, label="Prediction", lw=1)
ax_ts.plot(dates, target_ts, label="Target", lw=1)
ax_ts.set_ylabel("Value")
ax_ts.set_title(os.path.basename(args.pkl))
ax_ts.legend(loc="upper left")
ax_ts.xaxis.set_major_locator(mdates.YearLocator(5))
ax_ts.xaxis.set_minor_locator(mdates.YearLocator(1))
ax_ts.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.setp(ax_ts.get_xticklabels(), visible=False)  # hide top x labels (use bottom axis)

# Bottom-left: difference time series (target - prediction)
ax_diff = fig.add_subplot(gs[1, 0], sharex=ax_ts)
diff_ts = target_ts - prediction_ts
ax_diff.plot(dates, diff_ts, label="Target - Prediction", color="C2", lw=1)
ax_diff.axhline(0.0, color="k", linestyle="--", linewidth=0.6)
ax_diff.set_ylabel("Target - Pred")
ax_diff.set_xlabel("Time")
ax_diff.xaxis.set_major_locator(mdates.YearLocator(5))
ax_diff.xaxis.set_minor_locator(mdates.YearLocator(1))
ax_diff.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.setp(ax_diff.get_xticklabels(), rotation=45, ha="right")

# Right: prediction vs target scatter spanning both rows
ax_sc = fig.add_subplot(gs[:, 1])
# scatter: x = target, y = prediction
ax_sc.scatter(target_ts, prediction_ts, s=8, alpha=0.6)
# 1:1 line
mn = min(min(target_ts), min(prediction_ts))
mx = max(max(target_ts), max(prediction_ts))
ax_sc.plot([mn, mx], [mn, mx], "k--", linewidth=0.8)
ax_sc.set_xlabel("Target")
ax_sc.set_ylabel("Prediction")
ax_sc.set_title("Pred vs Target")
ax_sc.set_aspect("equal", adjustable="box")

plt.tight_layout()

out = args.out
if out is None:
    dname = os.path.dirname(args.pkl)
    base = os.path.splitext(os.path.basename(args.pkl))[0]
    out = os.path.join(dname, base + "_ts.webp")

fig.savefig(out, dpi=150, bbox_inches="tight")
print("Saved", out)

