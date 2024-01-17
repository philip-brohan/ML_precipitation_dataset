#!/usr/bin/env python

# Make raw data tensors for normalisation

import os
import sys

sDir = os.path.dirname(os.path.realpath(__file__))


def is_done(year, month):
    fn = "%s/MLP/raw_datasets/GPCP/blended/%04d-%02d.tfd" % (
        os.getenv("SCRATCH"),
        year,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


for year in range(1979, 2024):
    for month in range(1, 13):
        if is_done(year, month):
            continue
        cmd = "%s/make_training_tensor.py --year=%04d --month=%02d" % (
            sDir,
            year,
            month,
        )
        print(cmd)
