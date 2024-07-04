#!/usr/bin/env python

# Make all the normalization fits

import os

sDir = os.path.dirname(os.path.realpath(__file__))


def is_done(month, variable):
    fn = "%s/MLP/normalization/SPI_monthly/OCADA_tf_MM/%s/shape_m%02d.nc" % (
        os.getenv("SCRATCH"),
        variable,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


count = 0
for variable in ("ta", "slp", "precipi"):
    for month in range(1, 13):
        if is_done(month, variable):
            continue
        cmd = "%s/fit_for_month.py --month=%02d --variable=%s" % (
            sDir,
            month,
            variable,
        )
        print(cmd)
