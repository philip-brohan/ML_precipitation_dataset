#!/usr/bin/bash

echo './stripes.py --convolve=none --startyear=1850'
echo './stripes.py --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75'
echo './stripes.py --convolve=sub-11x13 --startyear=1850'
echo './stripes.py --reduce=mean --startyear=1850'
