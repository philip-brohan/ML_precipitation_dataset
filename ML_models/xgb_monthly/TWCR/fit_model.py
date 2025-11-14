#!/usr/bin/env python

# Fit XGBoost model to the extracted samples

import os
import sys
import xgboost as xgb

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--label",
    type=str,
    required=False,
    default='train',
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
if not os.path.isdir(opdir):
    os.makedirs(opdir)
if args.label is None:
    fname = "%s/TWCR.dt" % opdir
else:
    fname = "%s/TWCR_%s.dt" % (opdir,args.label)

dtrain=xgb.DMatrix(fname)

# Specify the model
# params = {
#     "objective": "reg:squarederror",   # Minimise squared error
#     "max_depth": 2,                    # Depth of tree
#     "eta": 1,                          # Learning rate
#     }
params = {
    "objective": "reg:squarederror",
    "booster": "gbtree",
    "eta": 0.1,                # smaller learning rate (was 1)
    "max_depth": 10,           # increase depth from 2
    "subsample": 0.8,         # row subsampling
    "colsample_bytree": 0.8,  # feature subsampling
    "min_child_weight": 1,    # control complexity
    "lambda": 5.0,            # L2 regularization
    "alpha": 1.0,             # L1 regularization
    "seed": 42,
    "verbosity": 1,
    "tree_method": "hist",   # uncomment for faster CPU training on large data
    # "tree_method": "gpu_hist" # use if you have GPU support and want GPU training
}

# Weight extreme values more than typical values
labels = dtrain.get_label()
weights = (labels-0.5)**2 +0.1
dtrain.set_weight(weights)

# fit the model
#bst = xgb.train(params,dtrain)
# Option A: use cross-validation to pick rounds
cvres = xgb.cv(
    params,
    dtrain,
    num_boost_round=1000,
    nfold=5,
    metrics=("rmse",),
    early_stopping_rounds=20,
    as_pandas=True,
    seed=42,
)
best_rounds = int(cvres["test-rmse-mean"].idxmin() + 1)

# fit the model with chosen rounds and show progress
bst = xgb.train(
    params,
    dtrain,
    num_boost_round=best_rounds,
    evals=[(dtrain, "train")],      # show training metrics; add validation DMatrix here if available
    verbose_eval=10,                # print metrics every 10 rounds (True prints every round)
    callbacks=[xgb.callback.ProgressBar()],  # optional progress bar (xgboost >= 1.6)
)

# Save the model
opdir = "%s/ML_models/xgb_monthly" % os.getenv('PDIR')
if not os.path.isdir(opdir):
    os.makedirs(opdir)
if args.mlabel is None:
    fname = "%s/TWCR.ubj" % opdir
else:
    fname = "%s/TWCR_%s.ubj" % (opdir,args.mlabel)

bst.save_model(fname)

