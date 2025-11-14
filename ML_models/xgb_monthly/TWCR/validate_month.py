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
import zarr

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
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
args = parser.parse_args()


# Get the data from the zarr arrays
def get_zarr(variable):
    fn = "%s/normalized_datasets/TWCR_tf_MM/%s_zarr" % (
        os.getenv("PDIR"),
        variable,
    )
    zarr_array = zarr.open(fn, mode="r")
    return zarr_array


t2m = get_zarr("TMP2m")
prmsl = get_zarr("PRMSL")
prate = get_zarr("PRATE")


# load the selected member, or ensemble mean for a month
def get_month(zf, year, month):
    d_idx = zf.attrs["AvailableMonths"]["%04d-%02d_00" % (year, month)]
    mnth = zf[:, :, :, d_idx]
    if args.member_idx is not None:
        mnth = mnth[:, :, args.member_idx]
    else:
        mnth = mnth.mean(axis=2)
    return mnth


# lat and long indices are the same for all fields
lat_idx = np.transpose(np.tile(np.arange(721, dtype=int), (1440, 1)))
lon_idx = np.tile(np.arange(1440, dtype=int), (721, 1))

# Source is a n*5 array containing 5 features:
#  pressure, temperature, latitude, longitude, month (all normalised)
# Target is an n*1 array containing one feature:
#  precipitation (normalised)
# we add args.sample rows to each array from each month
source = None
target = None

m_temperature = get_month(t2m, args.year, args.month).flatten()
if args.no_temperature:
    m_temperature = np.full_like(m_temperature, 0.5)
m_pressure = get_month(prmsl, args.year, args.month).flatten()
if args.no_pressure:
    m_pressure = np.full_like(m_pressure, 0.5)
m_precip = get_month(prate, args.year, args.month).flatten()
m_latitude = lat_idx.flatten() / 720
if args.fix_lat is not None:
    m_latitude = np.full_like(m_latitude, args.fix_lat/180 +0.5)
m_longitude = lon_idx.flatten() / 1440
if args.fix_lon is not None:
    m_longitude = np.full_like(m_longitude, args.fix_lon/360+0.5)
m_month = np.full_like(m_temperature, args.month)
if args.fix_month is not None:
    m_month = np.full_like(m_month, args.fix_month)
# Combine into feature array
m_source = np.column_stack(
    (m_pressure, m_temperature, m_latitude, m_longitude, m_month)
)
# Get this month's target similarly
precip = m_precip

source = xgb.DMatrix(data=m_source)

# Load the model
if args.mlabel is None:
    fname = "%s/TWCR.ubj" % opdir
else:
    fname = "%s/TWCR_%s.ubj" % (opdir, args.mlabel)

bst = xgb.Booster()
bst.load_model(fname)

preds = bst.predict(source)

# Layout: left = two panels (top: observed field, bottom: model), right = large scatter (spans both rows)
fig = plt.figure(figsize=(14, 6))
gs = fig.add_gridspec(2, 2, width_ratios=(1, 1), wspace=0.08, hspace=0.12)

ax_lt = fig.add_subplot(gs[0, 0])  # left top: observed field
ax_lb = fig.add_subplot(gs[1, 0])  # left bottom: model field
ax_r = fig.add_subplot(gs[:, 1])  # right: scatter spanning two rows

# reshape flattened arrays back to 2D
obs_grid = precip.reshape(721, 1440)
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

# plot model field (left bottom)
im2 = ax_lb.imshow(
    pred_grid,
    origin="lower",
    cmap=cmocean.cm.tarn,
    vmin=-0.25,
    vmax=1.25,
)
ax_lb.set_aspect(1)
ax_lb.set_title("Model")
ax_lb.set_xticks([])
ax_lb.set_yticks([])

# scatter / hexbin on the right (spanning both rows)
hb = ax_r.hexbin(precip, preds, gridsize=60, cmap="viridis", bins="log")
ax_r.plot(
    [precip.min(), precip.max()], [precip.min(), precip.max()], "k--", linewidth=0.8
)
ax_r.set_xlabel("Observed")
ax_r.set_ylabel("Predicted")
ax_r.set_title("%04d-%02d" % (args.year, args.month))
fig.colorbar(hb, ax=ax_r, label="log10(count)")

fig.savefig("monthly.webp", dpi=150, bbox_inches="tight")
