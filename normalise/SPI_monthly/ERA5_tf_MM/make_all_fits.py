#!/usr/bin/env python

# Make all the normalisation fits

import os


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
for variable in ("TMP2m", "PRMSL", "PRATE"):
    for month in range(1, 13):
        if is_done(month, variable):
            continue
        cmd = "./fit_for_month.py --month=%02d --variable=%s" % (
            month,
            variable,
        )
        print(cmd)
