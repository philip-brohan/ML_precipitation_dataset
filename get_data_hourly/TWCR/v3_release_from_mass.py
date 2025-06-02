#!/usr/bin/env python

# Retrieve archived 20CRv3 data from MASS

import sys
import os
import subprocess
import os.path
import glob
import re

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

# Base location for storage
mbase = "moose:/adhoc/projects/20cr/"
moose_dir = "%s/version_3/%04d" % (mbase, args.year)

# Disc data dir
ddir = "%s/20CR/version_3/" % (os.environ["PDIR"])
if not os.path.isdir(ddir):
    os.makedirs(ddir)


# Retrieve the observations
def retrieve_obs(year):
    # Are they on disc
    ofiles = glob.glob("%s/observations/%04d/%04d*.txt" % (ddir, year, year))
    if len(ofiles) > 100:
        print("Already on disc")
        return  # Already on disc

    proc = subprocess.Popen(
        "moo ls %s/observations_%04d.tgz" % (moose_dir, year),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if len(err) != 0:
        raise Exception(
            "Obs file not on mass %s/observations_%04d.tgz" % (moose_dir, year)
        )

    # Retrieve ob file from MASS
    ody = "%s/observations/%04d" % (ddir, year)
    if not os.path.isdir(ody):
        os.makedirs(ody)
    proc = subprocess.Popen(
        "moo get %s/observations_%04d.tgz %s/observations_%04d.tgz"
        % (moose_dir, year, ody, year),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if len(err) != 0:
        print(err)
        raise Exception("Failed to retrieve observations from %s" % moose_dir)
    otarf = "%s/observations/%04d/observations_%04d.tgz" % (ddir, year, year)
    proc = subprocess.Popen(
        "cd %s ; tar mxzf %s" % (ddir, otarf),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if len(err) != 0:
        print(err)
        raise Exception("Failed to untar %s" % otarf)

    # Clean up
    print("Done")
    os.remove(otarf)


# Retrieve a variable file
def retrieve_variable(year, variable):
    vf = "%s/%04d/%s.%04d_mem080.nc" % (ddir, year, variable, year)
    if os.path.isfile(vf):
        print("Already on disc")
        return  # Already on disc

    if not os.path.isdir("%s/%04d" % (ddir, year)):
        os.makedirs("%s/%04d" % (ddir, year))
    proc = subprocess.Popen(
        "moo get %s/%s_%04d.tar %s" % (moose_dir, variable, year, ddir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if len(err) != 0:
        print(err)
        raise Exception(
            "Failed to retrieve %s/%s_%04d.tar" % (moose_dir, variable, year)
        )
    otarf = "%s/%s_%04d.tar" % (ddir, variable, year)
    proc = subprocess.Popen(
        "cd %s ; tar mxf %s" % (ddir, otarf),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if len(err) != 0:
        print(err)
        raise Exception("Failed to untar %s" % otarf)

    # Clean up
    print("Done")
    os.remove(otarf)


if args.variable == "observations":
    retrieve_obs(args.year)
else:
    retrieve_variable(args.year, args.variable)
