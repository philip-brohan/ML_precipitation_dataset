#!/usr/bin/env python

# Turn samples from the normalized tensors into a DMatrix ready for XGBoost

import os
import sys
import xgboost as xgb
# Suppress warnings from TensorFlow - don't need a GPU for this
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from visualizations.stripes.TWCR.makeDataset import getDataset

import numpy as np
rng = np.random.default_rng()

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
    "--samples",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--member_idx",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--label",
    type=str,
    required=False,
    default=None,
)
args = parser.parse_args()

# Want temperature, precipitation and prate to model
t2m = getDataset(
        "TMP2m",
        startyear=args.start_year,
        endyear=args.end_year,
        cache=False,
        blur=None,
    )
prmsl = getDataset(
        "PRMSL",
        startyear=args.start_year,
        endyear=args.end_year,
        cache=False,
        blur=None,
    )
prate =  getDataset(
        "PRATE",
        startyear=args.start_year,
        endyear=args.end_year,
        cache=False,
        blur=None,
    )
ds = tf.data.Dataset.zip((t2m,prmsl,prate)).batch(1)

# Source is a n*5 array containing 5 features:
#  pressure, temperature, latitude, longitude, month (all normalised)
# Target is an n*1 array containing one feature:
#  precipitation (normalised)
# we add args.sample rows to each array from each month
source=None
target=None
for batch in ds:
    year = int(batch[0][1].numpy()[0][:4])
    month = int(batch[0][1].numpy()[0][5:7])
    member_idx = int(batch[0][1].numpy()[0][8:11])
    if args.member_idx is not None and member_idx != args.member_idx:
        continue
    if args.samples is not None:
        lat_idx = rng.choice(range(721), size=args.samples, replace=True)
        lon_idx = rng.choice(range(1440), size=args.samples, replace=True)
    else:
        raise Exception("Full array sampling not supported")
    # Get this month's sample from each of the source features
    m_temperature = batch[0][0].numpy()[0, lat_idx, lon_idx, 0].flatten()
    m_pressure = batch[1][0].numpy()[0, lat_idx, lon_idx, 0].flatten()
    m_latitude = lat_idx/720
    m_longitude = lon_idx/1440
    m_month = np.zeros((args.samples))+month
    m_source = np.column_stack((m_pressure,m_temperature,m_latitude,m_longitude,m_month))
    # Get this month's target similarly
    m_precip = batch[2][0].numpy()[0, lat_idx, lon_idx, 0].flatten()
    m_target = m_precip
    # Concatenate the monthly source and target onto the accumulator arrays
    if source is None:
        source = m_source
        target = m_target
    else:
        source = np.concatenate((source,m_source),axis=0)
        target = np.concatenate((target,m_target),axis=0)

# Save the files as xgboost DMatrix native
opdir = "%s/ML_models/xgb_monthly" % os.getenv('PDIR')
if not os.path.isdir(opdir):
    os.makedirs(opdir)
if args.label is None:
    fname = "%s/TWCR.dt" % opdir
else:
    fname = "%s/TWCR_%s.dt" % (opdir,args.label)

dtrain=xgb.DMatrix(data=source,label=target)
dtrain.save_binary(fname)