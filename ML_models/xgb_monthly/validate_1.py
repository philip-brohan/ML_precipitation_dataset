#!/usr/bin/env python

# Show the fit of an XGBoost model

import os
import sys
import xgboost as xgb

import matplotlib.pyplot as plt
import numpy as np

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--label",
    type=str,
    required=False,
    default=None,
)
parser.add_argument(
    "--mlabel",
    type=str,
    required=False,
    default=None,
)
parser.add_argument(
    "--out",
    type=str,
    required=False,
    default="validate1.webp",
)
args = parser.parse_args()

# Load the pre-prepared DMatrix
opdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")
fname = "%s/%s.dt" % (opdir, args.label)
dval = xgb.DMatrix(fname)

# Load the model
fname = "%s/%s.ubj" % (opdir, args.mlabel)

bst = xgb.Booster()
bst.load_model(fname)

y = dval.get_label()
preds = bst.predict(dval)

# correlation (ignore NaNs)
mask = (~np.isnan(y)) & (~np.isnan(preds))
if mask.sum() >= 2:
    corr = np.corrcoef(y[mask], preds[mask])[0, 1]
else:
    corr = float("nan")

# hexbin plot (predicted vs observed)
fig, ax = plt.subplots(figsize=(8, 6))
hb = ax.hexbin(y, preds, gridsize=60, cmap="viridis", bins="log")
ax.plot([y.min(), y.max()], [y.min(), y.max()], "k--", linewidth=0.8)
ax.set_xlabel("Observed")
ax.set_ylabel("Predicted")
cb = fig.colorbar(hb, ax=ax)
cb.set_label("log10(count)")
ax.text(
    0.05,
    0.95,
    f"r = {corr:.3f}",
    transform=ax.transAxes,
    va="top",
    ha="left",
    fontsize=10,
    bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"),
)
outf = args.out
fig.savefig(outf, dpi=150, bbox_inches="tight")
