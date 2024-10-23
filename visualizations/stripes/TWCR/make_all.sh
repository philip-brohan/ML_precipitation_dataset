#!/usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "$SCRIPT_DIR/stripes.py --variable=TMP2m --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=TMP2m --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --variable=TMP2m --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=TMP2m --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=TMP2m --reduce=mean --global_mean --annual_mean --vmin=0.25 --vmax=0.75 --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --variable=PRMSL --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=PRMSL --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --variable=PRMSL --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=PRMSL --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=PRMSL --reduce=mean --global_mean --annual_mean --vmin=0.35 --vmax=0.65 --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --variable=PRATE --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=PRATE --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --variable=PRATE --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=PRATE --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=PRATE --reduce=mean --global_mean --annual_mean --vmin=0.475 --vmax=0.525 --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --variable=SST --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=SST --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --variable=SST --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=SST --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=SST --reduce=mean --global_mean --annual_mean --vmin=0.25 --vmax=0.75 --startyear=1850"
