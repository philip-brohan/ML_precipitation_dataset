#!/usr/bin/env python

# Retrieve archived 20CRv3 data from NERSC

import sys
import os
import subprocess
import tarfile
import os.path

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument(
    "--variable",
    help="Variable name ('prmsl','observations,...)",
    type=str,
    required=True,
)
args = parser.parse_args()

print("Retrieving %s for %d" % (args.variable, args.year))

# Source URL at NERSC
remote_dir = (
    "https://portal.nersc.gov/archive/home/projects/incite11/www/"
    + "20C_Reanalysis_version_3/everymember_anal_netcdf/subdaily"
)

if args.variable == "observations":
    remote_file = (
        "https://portal.nersc.gov/m958/v3_observations/" + "%04d.zip"
    ) % args.year
else:
    remote_file = "%s/%s/%s_%04d.tar" % (
        remote_dir,
        args.variable,
        args.variable,
        args.year,
    )

# Disc data dir
ddir = "%s/20CR/version_3/hourly" % (os.environ["PDIR"])
if not os.path.isdir(ddir):
    os.makedirs(ddir)


def _get_data_dir(version="3"):
    """Return the root directory containing 20CR netCDF files"""
    g = "%s/20CR/version_%s/hourly/" % (os.environ["PDIR"], version)
    return g


def _get_data_file_name(variable, year, month=None, version="3", member=1):
    """Return the name of the file containing data for the
    requested variable, at the specified time, from the
    20CR version."""
    base_dir = _get_data_dir(version=version)
    # If monthly file exists, use that, otherwise, annual file
    if month is not None:
        name = "%s/%04d/%s.%04d%02d_mem%03d.nc" % (
            base_dir,
            year,
            variable,
            year,
            month,
            member,
        )
    if month is None or not os.path.isfile(name):
        name = "%s/%04d/%s.%04d_mem%03d.nc" % (
            base_dir,
            year,
            variable,
            year,
            member,
        )
    return name


def unpack_downloaded(variable, year):
    local_file = "%s/%s_%04d.tar" % (ddir, variable, year)
    tar = tarfile.open(local_file, "r")
    local_dir = os.path.dirname(local_file)
    tar.extractall(path=local_dir)
    tar.close()
    # Update the extracted file times
    #  To stop PDIR deleting them as too old
    nfiles = os.listdir("%s/%04d" % (local_dir, year))
    for nfile in nfiles:
        os.utime("%s/%04d/%s" % (local_dir, year, nfile))
    # os.remove(local_file)


def fetch(variable, year):

    local_file = _get_data_file_name(variable, year)

    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    # Download the tar file
    cmd = "wget -O %s %s" % (
        "%s/%s_%04d.tar" % (ddir, variable, year),
        remote_file,
    )
    wg_retvalue = subprocess.call(cmd, shell=True)
    if wg_retvalue != 0:
        raise Exception("Failed to retrieve data")
    unpack_downloaded(variable, year)


if args.variable == "observations":
    raise Exception("Obs not supported")
else:
    fetch(args.variable, args.year)
