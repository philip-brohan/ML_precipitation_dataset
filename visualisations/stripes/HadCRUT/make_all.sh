#!/usr/bin/bash

for convolve in none 12x12 sub-12x12
do
echo ./stripes.py --convolve=$convolve
done
echo ./stripes.py --reduce=mean
