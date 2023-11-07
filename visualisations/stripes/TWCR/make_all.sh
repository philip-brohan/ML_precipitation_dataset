#!/usr/bin/bash

for variable in TMP2m PRMSL PRATE SST
do
for convolve in none 11x13 sub-11x13
do
./stripes.py --variable=$variable --convolve=$convolve
done
./stripes.py --variable=$variable --reduce=mean
done
