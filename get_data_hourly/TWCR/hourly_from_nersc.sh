#!/usr/bin/bash

# Retrieve stored 20CRv3 data from nersc

for year in {1959..1860}
do
for var in PRMSL PRATE TMP2m TMPS UGRD10m VGRD10m
do 
#srun -t 3:00:00 
./v3_release_from_nersc.py --year=$year --variable=$var
done
done
 
