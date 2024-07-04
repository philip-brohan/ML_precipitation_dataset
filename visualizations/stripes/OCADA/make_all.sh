#!/usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "$SCRIPT_DIR/stripes.py --variable=ta --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=ta --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --variable=ta --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=ta --reduce=mean --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --variable=slp --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=slp --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --variable=slp --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=slp --reduce=mean --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --variable=precipi --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=precipi --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --variable=precipi --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=precipi --reduce=mean --startyear=1850"

