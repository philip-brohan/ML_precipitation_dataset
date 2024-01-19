#!/usr/bin/env python

# Get global mean series of normalised values and store as pickle

import os
import numpy as np
import tensorflow as tf
import pickle

sDir = os.path.dirname(os.path.realpath(__file__))

rng = np.random.default_rng()

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--source",
    help="Source dataset",
    type=str,
    required=True,
)
args = parser.parse_args()

if args.source == "ERA5":
    from ERA5Dataset import getDataset

    trainingData = getDataset(
        "total_precipitation",
        startyear=1950,
        endyear=2023,
        cache=False,
        blur=None,
    ).batch(1)
elif args.source == "TWCR":
    from TWCRDataset import getDataset

    trainingData = getDataset(
        "PRATE",
        startyear=1850,
        endyear=2023,
        cache=False,
        blur=None,
    ).batch(1)
elif args.source == "CRU":
    from CRUDataset import getDataset

    trainingData = getDataset(
        startyear=1850,
        endyear=2023,
        cache=False,
        blur=None,
    ).batch(1)
elif args.source == "GPCC_in-situ":
    from GPCC_in_situDataset import getDataset

    trainingData = getDataset(
        startyear=1850,
        endyear=2023,
        cache=False,
        blur=None,
    ).batch(1)
elif args.source == "GPCP":
    from GPCPDataset import getDataset

    trainingData = getDataset(
        startyear=1850,
        endyear=2023,
        cache=False,
        blur=None,
    ).batch(1)
else:
    raise Exception("Unsupported source " + args.source)

ndata = {}
members = np.zeros([1000])
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    try:
        member = int(batch[1].numpy()[0][8:11])
    except Exception:
        member = 0
    key = "%04d%02d%03d" % (year, month, member)
    members[member] += 1
    ndmo = batch[0].numpy().flatten()
    ndmo = ndmo[~np.isnan(ndmo)]
    ndmo = ndmo[ndmo != 0]
    ndata[key] = np.mean(ndmo)

# Fill in any gaps with np.nan
members = np.where(members != 0)
for year in range(1850, 2050):
    for month in range(1, 13):
        for member in members[0]:
            key = "%04d%02d%03d" % (year, month, member)
            if key not in ndata:
                ndata[key] = np.nan

print(ndata)
with open("%s/%s.pkl" % (sDir, args.source), "wb") as dfile:
    pickle.dump(ndata, dfile)
