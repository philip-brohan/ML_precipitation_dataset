#!/usr/bin/env python

# Make raw data tensors for normalisation

import os

sDir = os.path.dirname(os.path.realpath(__file__))


def is_done(year, month):
    fn = "%s/MLP/raw_datasets/GPCC/in_situ/%04d-%02d.tfd" % (
        os.getenv("SCRATCH"),
        year,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


for year in range(1891, 2019 + 1):
    for month in range(1, 13):
        if is_done(year, month):
            continue
        cmd = "%s/make_training_tensor.py --year=%04d --month=%02d" % (
            sDir,
            year,
            month,
        )
        print(cmd)
