#!/usr/bin/env python

# Plot a validation figure for the xgb model

# Show:
#  1) Target field
#  2) Model output
#  3) scatter plot

import os
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import cmocean
from utils import get_source_and_target, to_DMatrix

opdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Test year", type=int, required=False, default=1969)
parser.add_argument("--month", help="Test month", type=int, required=False, default=3)
parser.add_argument(
    "--member_idx", help="Member index (0-9)", type=int, required=False, default=None
)
parser.add_argument(
    "--mlabel",
    type=str,
    required=False,
    default=None,
)
parser.add_argument(
    "--source",
    type=str,  # 'TWCR','ERA5', or 'GC5'
    required=True,
    default=None,
)
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--no_uwind", action="store_true")
parser.add_argument("--no_vwind", action="store_true")
parser.add_argument("--no_humidity", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
parser.add_argument(
    "--out",
    type=str,
    required=False,
    default="monthly.webp",
)
args = parser.parse_args()

if args.source == "TWCR":
    from TWCR import get_month
elif args.source == "ERA5":
    from ERA5 import get_month
elif args.source == "GC5":
    from GC5 import get_month

# Source is a n*5 array containing 5 features:
#  pressure, temperature, latitude, longitude, month (all normalised)
# Target is an n*1 array containing one feature:
#  precipitation (normalised)

source, target = get_source_and_target(
    get_month,
    args.year,
    args.year,
    start_month=args.month,
    end_month=args.month,
    no_temperature=args.no_temperature,
    no_pressure=args.no_pressure,
    no_uwind=args.no_uwind,
    no_vwind=args.no_vwind,
    no_humidity=args.no_humidity,
    fix_lat=args.fix_lat,
    fix_lon=args.fix_lon,
    fix_month=args.fix_month,
)

dm = to_DMatrix(source, target)

# Load the model
fname = "%s/%s.ubj" % (opdir, args.mlabel)
bst = xgb.Booster()
bst.load_model(fname)

preds = bst.predict(dm)

# Layout: left = two panels (top: observed field, bottom: model field)
# Right column split into two: top = scatter, bottom = observation - model difference
fig = plt.figure(figsize=(14, 6))
# make the right column narrower so the scatter can be drawn with a 1:1 data aspect
gs = fig.add_gridspec(2, 2, width_ratios=(1, 0.8), wspace=0.08, hspace=0.12)

ax_lt = fig.add_subplot(gs[0, 0])  # left top: observed field
ax_lb = fig.add_subplot(gs[1, 0])  # left bottom: model field
ax_r_top = fig.add_subplot(gs[0, 1])  # right top: obs - model diff (swapped)
ax_r_bot = fig.add_subplot(gs[1, 1])  # right bottom: scatter (swapped)

# reshape flattened arrays back to 2D
obs_grid = target.reshape(721, 1440)
pred_grid = preds.reshape(721, 1440)

# plot observed field (left top)
im1 = ax_lt.imshow(
    obs_grid,
    origin="lower",
    cmap=cmocean.cm.tarn,
    vmin=-0.25,
    vmax=1.25,
)
ax_lt.set_aspect(1)
ax_lt.set_title("Observed")
ax_lt.set_xticks([])
ax_lt.set_yticks([])
fig.colorbar(im1, ax=ax_lt, fraction=0.046, pad=0.02)

# plot model field (left bottom)
im2 = ax_lb.imshow(
    pred_grid,
    origin="lower",
    cmap=cmocean.cm.tarn,
    vmin=-0.25,
    vmax=1.25,
)
ax_lb.set_aspect(1)
ax_lb.set_title("Predicted")
ax_lb.set_xticks([])
ax_lb.set_yticks([])
fig.colorbar(im2, ax=ax_lb, fraction=0.046, pad=0.02)

# difference field (right top) = observed - model (use same colormap and data range)
diff_grid = obs_grid - pred_grid
im3 = ax_r_top.imshow(
    diff_grid,
    origin="lower",
    cmap=cmocean.cm.tarn,  # use same colormap as observed/model
    vmin=-0.75,
    vmax=0.755,  # data range as im1/im2, but centred on 0
)
ax_r_top.set_aspect("equal", adjustable="box")
ax_r_top.set_title("Difference")
ax_r_top.set_xticks([])
ax_r_top.set_yticks([])
fig.colorbar(im3, ax=ax_r_top, fraction=0.046, pad=0.02)

# scatter (right bottom) (moved to bottom)
hb = ax_r_bot.hexbin(target, preds, gridsize=60, cmap="viridis", bins="log")
ax_r_bot.plot(
    [target.min(), target.max()], [target.min(), target.max()], "k--", linewidth=0.8
)
ax_r_bot.set_xlabel("Observed")
ax_r_bot.set_ylabel("Predicted")
ax_r_bot.set_title("%04d-%02d" % (args.year, args.month))

# correlation coefficient (ignore NaNs)
mask = (~np.isnan(target)) & (~np.isnan(preds))
if mask.sum() >= 2:
    corr = np.corrcoef(target[mask], preds[mask])[0, 1]
else:
    corr = float("nan")
ax_r_bot.text(
    0.05,
    0.95,
    f"r = {corr:.3f}",
    transform=ax_r_bot.transAxes,
    va="top",
    ha="left",
    fontsize=10,
    bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"),
)

fig.colorbar(hb, ax=ax_r_bot, label="log10(count)", fraction=0.046, pad=0.02)

# Revert manual positioning: put the scatter axis back into its GridSpec slot
ax_r_bot.set_position(gs[1, 1].get_position(fig))
ax_r_bot.set_aspect("equal", adjustable="box")

# after creating/plotting ax_r_bot (the scatter axis), keep its size/shape but center it horizontally in the right column
col_bbox = gs[:, 1].get_position(fig)
col_x0, col_w = col_bbox.x0, col_bbox.width

cur_bbox = ax_r_bot.get_position()
cur_y0, cur_h, cur_w = cur_bbox.y0, cur_bbox.height, cur_bbox.width

# new x so the axis is centred horizontally in the right column, keep same width/height
new_x0 = col_x0 + 0.5 * (col_w - cur_w)
ax_r_bot.set_position([new_x0, cur_y0, cur_w, cur_h])

fig.savefig(args.out, dpi=150, bbox_inches="tight")
