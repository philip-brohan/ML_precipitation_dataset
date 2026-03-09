#!/usr/bin/bash

# Store downloaded 20CRv3 data on MASS

for year in {1840..1850}
do
for var in PRMSL PRATE TMP2m TMPS UGRD10m VGRD10m
do 
#srun -t 1:00:00 
./v3_release_to_mass.py --year=$year --variable=$var
done
done
