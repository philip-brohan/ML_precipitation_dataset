#!/usr/bin/env python

# Retrieve OCADA monthly average ensemble means

import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--variable", help="Variable name", type=str, default="precipi")
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/OCADA/monthly/means" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir, exist_ok=True)


def remote_name(variable, year):
    return (
        "https://climate.mri-jma.go.jp/pub/archives/Ishii-et-al_OCADA/mean/sfc_avr_mon/%s/%s_%04d.nc"
        % (variable, variable, year)
    )


def local_name(variable, year):
    return "%s/%s_%04d.nc" % (args.opdir, variable, year)


# Download the .nc file
cmd = "wget -O %s %s" % (
    local_name(args.variable, args.year),
    remote_name(args.variable, args.year),
)
wg_retvalue = subprocess.call(cmd, shell=True)
if wg_retvalue != 0:
    raise Exception("Failed to retrieve data")
