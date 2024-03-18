#!/usr/bin/env python

# Make normalised data tensors for analysis

import os
from get_data.HadCRUT import HadCRUT

sDir = os.path.dirname(os.path.realpath(__file__))


def is_done(year, month, member):
    fn = "%s/MLP/normalised_datasets/HadCRUT_tf_MM/T/%04d-%02d_%03d.tfd" % (
        os.getenv("SCRATCH"),
        year,
        month,
        member,
    )
    if os.path.exists(fn):
        return True
    return False


for year in range(1850, 2024):
    for month in range(1, 13):
        for member in HadCRUT.members:
            if is_done(year, month, member):
                continue
            cmd = "%s/make_training_tensor.py --year=%04d --month=%02d --member=%d" % (
                sDir,
                year,
                month,
                member,
            )
            print(cmd)
