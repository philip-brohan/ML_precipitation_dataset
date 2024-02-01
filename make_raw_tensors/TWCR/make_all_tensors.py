#!/usr/bin/env python

# Make raw data tensors for normalisation

import os
import argparse

sDir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--variable",
    help="Variable name",
    type=str,
    required=True,
)
args = parser.parse_args()


def is_done(year, month, variable, member):
    fn = "%s/MLP/raw_datasets/TWCR/%s/%02d/%04d-%02d.tfd" % (
        os.getenv("SCRATCH"),
        variable,
        member,
        year,
        month,
    )
    if os.path.exists(fn):
        return True
    return False


for year in range(1850, 2014):
    for month in range(1, 13):
        for member in range(1, 81):
            if is_done(year, month, args.variable, member):
                continue
            cmd = (
                "%s/make_training_tensor.py --year=%04d --month=%02d --variable=%s --member=%d"
                % (
                    sDir,
                    year,
                    month,
                    args.variable,
                    member,
                )
            )
            print(cmd)
