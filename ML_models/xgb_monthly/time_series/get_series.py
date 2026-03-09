#!/usr/bin/env python

# Get global mean series of normalized values and store as pickle

import os
import iris
import numpy as np

# Suppress warnings from TensorFlow - don't need a GPU for this
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
import pickle
from utilities.grids import E5sCube_grid_areas

rng = np.random.default_rng()

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--source",
    help="Source dataset",
    type=str,
    required=False,
    default=None,
)
parser.add_argument(
    "--label",
    help="Model label",
    type=str,
    required=False,
    default=None,
)
parser.add_argument(
    "--rchoice",
    help="Area reduction choice (None or 'area')",
    type=str,
    required=False,
    default=None,
)
parser.add_argument(
    "--mask_file",
    help="File containing averaging data mask",
    type=str,
    required=False,
    default=None,
)
args = parser.parse_args()

# Load the mask file if provided
if args.mask_file is not None:
    mask = iris.load_cube(
        "%s/visualizations/time_series/masks/%s.nc"
        % (os.getenv("PDIR"), args.mask_file)
    )

if args.source is not None:
    if args.label is not None:
        raise Exception("Cannot use both source and model arguments")
    if args.source == "ERA5":
        from visualizations.stripes.ERA5.makeDataset import getDataset

        trainingData = getDataset(
            "total_precipitation",
            startyear=1950,
            endyear=2023,
            cache=False,
            blur=None,
        ).batch(1)
    elif args.source == "TWCR":
        from visualizations.stripes.TWCR.makeDataset import getDataset

        trainingData = getDataset(
            "PRATE",
            startyear=1850,
            endyear=2023,
            cache=False,
            blur=None,
        ).batch(1)
    elif args.source == "GC5":
        from visualizations.stripes.GC5.makeDataset import getDataset

        trainingData = getDataset(
            "prate",
            startyear=1850,
            endyear=2023,
            cache=False,
            blur=None,
        ).batch(1)
    elif args.source == "CRU":
        from visualizations.stripes.CRU.makeDataset import getDataset

        trainingData = getDataset(
            startyear=1850,
            endyear=2023,
            cache=False,
            blur=None,
        ).batch(1)
    elif args.source == "GPCC_in-situ":
        from visualizations.stripes.GPCC.in_situ.makeDataset import getDataset

        trainingData = getDataset(
            startyear=1850,
            endyear=2023,
            cache=False,
            blur=None,
        ).batch(1)
    elif args.source == "GPCP":
        from visualizations.stripes.GPCP.makeDataset import getDataset

        trainingData = getDataset(
            startyear=1850,
            endyear=2023,
            cache=False,
            blur=None,
        ).batch(1)
    else:
        raise Exception("Unsupported source " + args.source)
if args.label is not None:
    if args.source is not None:
        raise Exception("Cannot use both source and label arguments")
    from ML_models.xgb_monthly.stripes.makeDataset import getDataset

    trainingData = getDataset(
        args.label,
        startyear=1850,
        endyear=2023,
    ).batch(1)


def latlon_reduce(choice, ndata):
    ndata[~np.isfinite(ndata)] = 0
    if args.mask_file is not None:
        ndata[mask.data == 0] = 0
    if choice is None:
        ndata = ndata.flatten()
        ndata = ndata[ndata != 0]
        return np.mean(ndata)
    elif choice == "area":
        gweight = E5sCube_grid_areas
        gweight = np.ma.MaskedArray(gweight, ndata == 0)
        ndata_sum = np.sum(ndata * gweight)
        gweight_sum = np.sum(gweight)
        ndata_mean = ndata_sum / gweight_sum
        return ndata_mean
    else:
        raise Exception("Unsupported latlon_reduce choice %s" % choice)


ndata = {}
members = np.zeros([1000])
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    member = 0
    if args.source == "TWCR":
        member = int(batch[1].numpy()[0][8:11])
    if args.source == "GC5":
        member = int(batch[1].numpy()[0][10:13]) - 339  # Convert 'dl339,dl340, -> 0,1,
    key = "%04d%02d%03d" % (year, month, member)
    members[member] += 1
    ndmo = batch[0].numpy().squeeze()
    ndata[key] = latlon_reduce(args.rchoice, ndmo)


# Fill in any gaps with np.nan
members = np.where(members != 0)
for year in range(1850, 2050):
    for month in range(1, 13):
        for member in members[0]:
            key = "%04d%02d%03d" % (year, month, member)
            if key not in ndata:
                ndata[key] = np.nan

if args.rchoice is None:
    args.rchoice = "None"
if args.mask_file is None:
    args.mask_file = "None"
else:
    args.mask_file = os.path.splitext(os.path.basename(args.mask_file))[0]

opdir = "%s/ML_models/xgb_monthly/" % os.getenv("PDIR")
if args.source is not None:
    opdir += "sources/%s" % args.source
else:
    opdir += "/%s/series" % args.label
if not os.path.isdir(opdir):
    os.makedirs(opdir)

with open(
    "%s/%s_%s_%s.pkl" % (opdir, args.mask_file, args.rchoice, args.source), "wb"
) as dfile:
    pickle.dump(ndata, dfile)
