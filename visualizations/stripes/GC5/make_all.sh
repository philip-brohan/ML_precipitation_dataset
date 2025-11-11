#!/usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "$SCRIPT_DIR/stripes.py --variable=t2m --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=t2m --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --variable=t2m --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=t2m --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=t2m --reduce=mean --global_mean --annual_mean --vmin=0.25 --vmax=0.75 --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --variable=prate --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=prate --convolve=11x13 --startyear=1850 --vmin=0.35 --vmax=0.65"
echo "$SCRIPT_DIR/stripes.py --variable=prate --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=prate --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=prate --reduce=mean --global_mean --annual_mean --vmin=0.48 --vmax=0.52 --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --variable=prmsl --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=prmsl --convolve=11x13 --startyear=1850 --vmin=0.35 --vmax=0.65"
echo "$SCRIPT_DIR/stripes.py --variable=prmsl --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=prmsl --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --variable=prmsl --reduce=mean --global_mean --annual_mean --vmin=0.48 --vmax=0.52 --startyear=1850"

for run in dl339 dl340 dl341
do
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=t2m --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=t2m --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=t2m --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=t2m --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=t2m --reduce=mean --global_mean --annual_mean --vmin=0.25 --vmax=0.75 --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prate --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prate --convolve=11x13 --startyear=1850 --vmin=0.35 --vmax=0.65"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prate --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prate --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prate --reduce=mean --global_mean --annual_mean --vmin=0.48 --vmax=0.52 --startyear=1850"

echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prmsl --convolve=none --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prmsl --convolve=11x13 --startyear=1850 --vmin=0.35 --vmax=0.65"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prmsl --convolve=sub-11x13 --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prmsl --reduce=mean --startyear=1850"
echo "$SCRIPT_DIR/stripes.py --run=$run --variable=prmsl --reduce=mean --global_mean --annual_mean --vmin=0.48 --vmax=0.52 --startyear=1850"
done
