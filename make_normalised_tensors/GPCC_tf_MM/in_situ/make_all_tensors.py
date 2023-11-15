#!/usr/bin/env python

# Make normalised data tensors for analysis

import os


def is_done(year, month):
    fn = "%s/MLP/normalised_datasets/GPCC_tf_MM/in_situ/%04d-%02d.tfd" % (
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
        cmd = "./make_training_tensor.py --year=%04d --month=%02d" % (
            year,
            month,
        )
        print(cmd)
