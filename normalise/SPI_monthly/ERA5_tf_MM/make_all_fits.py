#!/usr/bin/env python

# Make all the normalisation fits

import os


def is_done(month, variable):
    fn = "%s/MLP/normalisation/SPI_monthly/ERA5_tf_MM/%s/shape_m%02d.nc" % (
        os.getenv("SCRATCH"),
        variable,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


count = 0
for variable in ("2m_temperature", "mean_sea_level_pressure", "total_precipitation"):
    for month in range(1, 13):
        if is_done(month, variable):
            continue
        cmd = "./fit_for_month.py --month=%02d --variable=%s" % (
            month,
            variable,
        )
        print(cmd)
