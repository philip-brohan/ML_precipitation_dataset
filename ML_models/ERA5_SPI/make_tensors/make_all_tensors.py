#!/usr/bin/env python

# Make 62 years of monthly-data tensors

import os

from ML_models.ERA5_SPI.localise import ModelName


def is_done(year, month, purpose):
    fn = "%s/MLP/%s/datasets/%s/%04d-%02d.tfd" % (
        os.getenv("SCRATCH"),
        ModelName,
        purpose,
        year,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


count = 0
for year in range(1940, 2023):
    for month in range(1, 13):
        purpose = "training"
        count += 1
        if count % 11 == 0:
            purpose = "test"
        if is_done(year, month, purpose):
            continue
        cmd = "./make_training_tensor.py --year=%04d --month=%02d" % (
            year,
            month,
        )
        if purpose == "test":
            cmd += " --test"
        print(cmd)
