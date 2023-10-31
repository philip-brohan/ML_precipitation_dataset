#!/usr/bin/bash

for variable in 2m_temperature mean_sea_level_pressure total_precipitation sea_surface_temperature
do
for convolve in none 12x12 sub-12x12
do
./stripes.py --variable=$variable --convolve=$convolve
done
./stripes.py --variable=$variable --reduce=mean
done
