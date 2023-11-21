#!/usr/bin/bash

echo './stripes.py --variable=2m_temperature --convolve=none --startyear=1850'
echo './stripes.py --variable=2m_temperature --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75'
echo './stripes.py --variable=2m_temperature --convolve=sub-11x13 --startyear=1850'
echo './stripes.py --variable=2m_temperature --reduce=mean --startyear=1850'

echo './stripes.py --variable=mean_sea_level_pressure --convolve=none --startyear=1850'
echo './stripes.py --variable=mean_sea_level_pressure --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75'
echo './stripes.py --variable=mean_sea_level_pressure --convolve=sub-11x13 --startyear=1850'
echo './stripes.py --variable=mean_sea_level_pressure --reduce=mean --startyear=1850'

echo './stripes.py --variable=total_precipitation --convolve=none --startyear=1850'
echo './stripes.py --variable=total_precipitation --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75'
echo './stripes.py --variable=total_precipitation --convolve=sub-11x13 --startyear=1850'
echo './stripes.py --variable=total_precipitation --reduce=mean --startyear=1850'

echo './stripes.py --variable=sea_surface_temperature --convolve=none --startyear=1850'
echo './stripes.py --variable=sea_surface_temperature --convolve=11x13 --startyear=1850 --vmin=0.25 --vmax=0.75'
echo './stripes.py --variable=sea_surface_temperature --convolve=sub-11x13 --startyear=1850'
echo './stripes.py --variable=sea_surface_temperature --reduce=mean --startyear=1850'
