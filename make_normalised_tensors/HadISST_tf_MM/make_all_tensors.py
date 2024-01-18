#!/usr/bin/env python

# Make normalised data tensors for analysis

import os

sDir = os.path.dirname(os.path.realpath(__file__))


def is_done(year, month):
    fn = "%s/MLP/normalised_datasets/HadISST_tf_MM/v1/%04d-%02d.tfd" % (
        os.getenv("SCRATCH"),
        year,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


for year in range(1870, 2024):
    for month in range(1, 13):
        if is_done(year, month):
            continue
        cmd = "%s/make_training_tensor.py --year=%04d --month=%02d" % (
            sDir,
            year,
            month,
        )
        print(cmd)
