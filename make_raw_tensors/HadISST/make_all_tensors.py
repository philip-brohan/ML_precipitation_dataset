#!/usr/bin/env python

# Make raw data tensors for normalisation

import os
from get_data.HadISST.v1 import HadISST


def is_done(year, month):
    fn = "%s/MLP/raw_datasets/HadISST/v1/%04d-%02d.tfd" % (
        os.getenv("SCRATCH"),
        year,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


for year in range(1871, 2024):
    for month in range(1, 13):
        if is_done(year, month):
            continue
        cmd = "./make_training_tensor.py --year=%04d --month=%02d" % (
            year,
            month,
        )
        print(cmd)
