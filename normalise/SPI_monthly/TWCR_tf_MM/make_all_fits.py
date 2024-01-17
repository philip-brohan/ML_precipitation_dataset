#!/usr/bin/env python

# Make all the normalisation fits

import os

sDir = os.path.dirname(os.path.realpath(__file__))

def is_done(month, variable):
    fn = "%s/MLP/normalisation/SPI_monthly/TWCR_tf_MM/%s/shape_m%02d.nc" % (
        os.getenv("SCRATCH"),
        variable,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


count = 0
for variable in ("TMP2m", "PRMSL", "PRATE", "SST"):
    for month in range(1, 13):
        if is_done(month, variable):
            continue
        cmd = "%s/fit_for_month.py --month=%02d --variable=%s" % (
            sDir,
            month,
            variable,
        )
        print(cmd)
