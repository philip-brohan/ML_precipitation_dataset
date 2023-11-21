#!/usr/bin/env python

# Make all the normalisation fits

import os


def is_done(month):
    fn = "%s/MLP/normalisation/SPI_monthly/GPCC_tf_MM/blended/shape_m%02d.nc" % (
        os.getenv("SCRATCH"),
        month,
    )
    if os.path.exists(fn):
        return True
    return False


for month in range(1, 13):
    if is_done(month):
        continue
    cmd = "./fit_for_month.py --month=%02d" % (month,)
    print(cmd)
