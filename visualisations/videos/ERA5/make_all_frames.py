#!/usr/bin/env python

# Make all the individual frames

import os
import numpy as np
import datetime

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=False, default=1950)
parser.add_argument("--endyear", type=int, required=False, default=2023)
parser.add_argument("--variable", help="Variable", type=str, required=True)
parser.add_argument(
    "--intermediate",
    help="No of interpolated frames between months",
    type=int,
    required=False,
    default=6,
)
args = parser.parse_args()

opdir = "%s/MLP/normalised_datasets/ERA5_tf_MM/videos/%s" % (
    os.getenv("SCRATCH"),
    args.variable,
)


# Function to check if the job is already done for this month
def is_done(year, month):
    ny = year
    nm = month + 1
    if nm > 12:
        ny += 1
        nm = 1
    tdts = datetime.datetime(year, month, 15, 0)
    ndt = datetime.datetime(ny, nm, 15, 0)
    dt_points = np.linspace(
        tdts.timestamp(), ndt.timestamp(), args.intermediate, endpoint=False
    )
    for dtp in dt_points:
        dtm = datetime.date.fromtimestamp(dtp)
        op_file_name = ("%s/%04d-%02d-%02d.png") % (
            opdir,
            dtm.year,
            dtm.month,
            dtm.day,
        )
        if not os.path.isfile(op_file_name):
            return False
    return True


for year in range(args.startyear, args.endyear + 1):
    for month in range(1, 13):
        if is_done(year, month):
            continue
        cmd = ("./frame.py --year=%d --month=%d --intermediate=%d --variable=%s") % (
            year,
            month,
            args.intermediate,
            args.variable,
        )
        print(cmd)
