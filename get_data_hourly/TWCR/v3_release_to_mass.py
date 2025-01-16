#!/usr/bin/env python

# Archive 20CRv3 data - downloaded from NERSC - to MASS

import sys
import os
import subprocess
import os.path
import glob
import tarfile

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

print("Storing %s for %d" % (args.variable, args.year))

# Base location for storage
mbase = "moose:/adhoc/projects/20cr/"
moose_dir = "%s/version_3/%04d" % (mbase, args.year)

# Disc data dir
ddir = "%s/20CR/version_3/" % (os.environ["SCRATCH"])
if not os.path.isdir(ddir):
    os.makedirs(ddir)


# Store a variable file
def store_variable(year, var):
    vf = "%s/%s_%04d.tar" % (moose_dir, var, year)
    proc = subprocess.Popen(
        "moo test %s" % vf,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if len(err) != 0:
        print(err)
        raise Exception("Failed to test %s - moose problem?" % vf)
    if out == b"true\n":
        print("%s is already on MASS" % vf)
        return  # Already on disc

    # Are there any fields to archive?
    ofiles = glob.glob("%s/%04d/%s.%04d_mem*.nc" % (ddir, year, var, year))
    if len(ofiles) == 0:  # No fields on disc
        raise Exception("No %s fields on disc for %04d v3" % (var, year))

    # Pack the month's fields into a single file
    otarf = "%s/%04d/%s_%04d.tar" % (ddir, year, var, year)
    tf = tarfile.open(name=otarf, mode="w")
    blen = len(ddir)
    for of in ofiles:
        tf.add(of, arcname=of[blen:])
    tf.close()

    # Make the MASS directory - if already made this will just fail harmlessly
    proc = subprocess.Popen(
        "moo mkdir %s " % moose_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()  # Ignore the result

    # Put the tar file on MASS
    proc = subprocess.Popen(
        "moo put %s %s/" % (otarf, moose_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    (out, err) = proc.communicate()
    if len(err) != 0:
        print(err)
        raise Exception("Failed to store %s" % (otarf))

    # Clean up
    print("Done")
    os.remove(otarf)


if args.variable == "observations":
    raise Exception("Observations not yet supported")
else:
    store_variable(args.year, args.variable)
