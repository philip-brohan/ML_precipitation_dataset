#!/usr/bin/env python

# Show the fit of an XGBoost model

import os
import sys
import xgboost as xgb
import matplotlib.pyplot as plt


import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--label",
    type=str,
    required=False,
    default='test',
)
parser.add_argument(
    "--mlabel",
    type=str,
    required=False,
    default=None,
)
args = parser.parse_args()

# Load the pre-prepared DMatrix 
opdir = "%s/ML_models/xgb_monthly" % os.getenv('PDIR')
if args.label is None:
    fname = "%s/TWCR.dt" % opdir
else:
    fname = "%s/TWCR_%s.dt" % (opdir,args.label)

dval=xgb.DMatrix(fname)

# Load the model
if args.mlabel is None:
    fname = "%s/TWCR.ubj" % opdir
else:
    fname = "%s/TWCR_%s.ubj" % (opdir,args.mlabel)

bst=xgb.Booster()
bst.load_model(fname)

y = dval.get_label()
preds = bst.predict(dval)

# hexbin plot (predicted vs observed)
fig, ax = plt.subplots(figsize=(8, 6))
hb = ax.hexbin(y, preds, gridsize=60, cmap='viridis', bins='log')
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', linewidth=0.8)
ax.set_xlabel('Observed')
ax.set_ylabel('Predicted')
cb = fig.colorbar(hb, ax=ax)
cb.set_label('log10(count)')
outf = os.path.join("./", "validate1.webp")
fig.savefig(outf, dpi=150, bbox_inches='tight')
