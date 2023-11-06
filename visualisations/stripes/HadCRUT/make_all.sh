#!/usr/bin/bash

for convolve in none 11x13 sub-11x13
do
echo ./stripes.py --convolve=$convolve
done
echo ./stripes.py --reduce=mean
