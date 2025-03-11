#!/usr/bin/env python

# Make all the normalization fits

import os
import datetime

sDir = os.path.dirname(os.path.realpath(__file__))


def is_done(month, day, hour, variable):
    fn = "%s/MLP/normalization/SPI_hourly/TWCR_tf_MM/%s/shape_m%02d_d%02d_h%02d.nc" % (
        os.getenv("SCRATCH"),
        variable,
        month,
        day,
        hour,
    )
    if os.path.exists(fn):
        return True
    return False


count = 0
for variable in ("TMP2m", "PRMSL", "PRATE", "SST"):
    for month in range(1, 13):
        for day in range(1, 32):
            try:
                dtte = datetime.datetime(1950, month, day, 0)
            except ValueError:
                continue  # Some months have fewer than 31 days
            for hour in range(0, 24, 3):
                if is_done(month, day, hour, variable):
                    continue
                cmd = (
                    "%s/fit_for_month.py --month=%02d --day=%02d --hour=%02d --variable=%s"
                    % (
                        sDir,
                        month,
                        day,
                        hour,
                        variable,
                    )
                )
                cmd += " --startyear=1961 --endyear=1990"
                print(cmd)
