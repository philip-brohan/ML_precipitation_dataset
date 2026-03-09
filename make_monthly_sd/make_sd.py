#!/usr/bin/env python

# Load all the hourly data for a variable/year
# calculate the standard deviation for each ensemble member/month
# save as a monthly file.

import os
import sys
import iris
import iris.cube
import argparse

# Make iris less irritating

import warnings

msg = r"Cannot check if coordinate is contiguous: Invalid operation for 'time'"
warnings.filterwarnings("ignore", message=msg)

iris.FUTURE.save_split_attrs = True

# command-line arguments - variable and month
parser = argparse.ArgumentParser(
    description="Calculate monthly standard deviation for each ensemble member"
)
parser.add_argument("--variable", type=str, help="Variable name (e.g., TMP2m)")
parser.add_argument("--year", type=int, help="Year (e.g., 2020)")
args = parser.parse_args()

for member in range(1, 81):
    pdir = os.getenv("PDIR")
    output_file = f"{pdir}/20CR/version_3/monthly/members/{args.year:04d}/{args.variable}.{args.year}.sd_mem{member:03d}.nc"
    # Check if already done
    if os.path.isfile(output_file):
        print(
            f"Output file {output_file} already exists. Skipping year {args.year} member {member}."
        )
        continue

    # Construct the input file path
    input_file = f"{pdir}/20CR/version_3/hourly/{args.year:04d}/{args.variable}.{args.year}_mem{member:03d}.nc"

    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(
            f"Input file {input_file} does not exist. Skipping year {args.year} member {member}."
        )
        continue

    sds = iris.cube.CubeList()
    for month in range(1, 13):
        # Load the hourly data (using iris)
        constraint = iris.Constraint(time=lambda cell: cell.point.month == month)
        try:
            cube = iris.load_cube(input_file, constraint)
        except Exception as e:
            print(f"Error loading {input_file} {month}: {e}")
            continue
        # Calculate the standard deviation across the time dimension
        try:
            sd_cube = cube.collapsed("time", iris.analysis.STD_DEV)
        except Exception as e:
            print(f"Error calculating standard deviation for {input_file} {month}: {e}")
            continue
        sds.append(sd_cube)

    # Concatenate the monthly standard deviation cubes into a single cube for the year
    try:
        yearly_sd_cube = iris.cube.CubeList(sds).merge_cube()
    except Exception as e:
        print(f"Error concatenating cubes for {input_file}: {e}")
        continue
    # Save the yearly standard deviation cube to a new file
    try:
        iris.save(yearly_sd_cube, output_file)
        print(f"Saved monthly standard deviation to {output_file}")
    except Exception as e:
        print(f"Error saving {output_file}: {e}")
        continue
