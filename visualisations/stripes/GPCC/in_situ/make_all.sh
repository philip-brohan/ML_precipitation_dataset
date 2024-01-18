#!/usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "$SCRIPT_DIR/stripes.py --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --reduce=mean --startyear=1850"
