#!/usr/bin/env python

# Compare two model fits

import os
import sys
import xgboost as xgb
import matplotlib.pyplot as plt
import numpy as np


import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--label1",
    type=str,
    required=True,
)
parser.add_argument(
    "--mlabel1",
    type=str,
    required=True,
)
parser.add_argument(
    "--label2",
    type=str,
    required=True,
)
parser.add_argument(
    "--mlabel2",
    type=str,
    required=True,
)
parser.add_argument(
    "--out",
    type=str,
    required=False,
    default='validate2.webp',
)
args = parser.parse_args()

# Load a model and data
opdir = "%s/ML_models/xgb_monthly" % os.getenv("PDIR")


def load_model_and_data(label, mlabel):
    fname = "%s/%s.dt" % (opdir, label)
    dval = xgb.DMatrix(fname)
    fname = "%s/%s.ubj" % (opdir, mlabel)
    bst = xgb.Booster()
    bst.load_model(fname)
    return bst, dval


# Load both models + data
bst1, dval1 = load_model_and_data(args.label1, args.mlabel1)
bst2, dval2 = load_model_and_data(args.label2, args.mlabel2)

# get labels and predictions for each
y1, preds1 = dval1.get_label(), bst1.predict(dval1)
y2, preds2 = dval2.get_label(), bst2.predict(dval2)

# two panels side-by-side
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharex=False, sharey=False)

for ax, y, preds, title in zip(
    axes,
    (y1, y2),
    (preds1, preds2),
    (
        f"{args.mlabel1 or 'default'} : {args.label1}",
        f"{args.mlabel2 or 'default'}: {args.label2}",
    ),
):
    hb = ax.hexbin(y, preds, gridsize=60, cmap="viridis", bins="log")
    ax.plot([y.min(), y.max()], [y.min(), y.max()], "k--", linewidth=0.8)
    ax.set_xlabel("Observed")
    ax.set_ylabel("Predicted")
    ax.set_title(title)

    # correlation coefficient (ignore NaNs)
    mask = (~np.isnan(y)) & (~np.isnan(preds))
    if mask.sum() >= 2:
        corr = np.corrcoef(y[mask], preds[mask])[0, 1]
    else:
        corr = float("nan")
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

# single shared colorbar for both panels
fig.colorbar(hb, ax=axes.ravel().tolist(), label="log10(count)")

fig.savefig(args.out, dpi=150, bbox_inches="tight")
