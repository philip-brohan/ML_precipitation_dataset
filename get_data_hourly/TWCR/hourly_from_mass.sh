#!/usr/bin/bash

# Retrieve stored 20CRv3 data from MASS

for year in {1969..2009}
do
for var in PRMSL PRATE TMP2m TMPS UGRD10m VGRD10m observations
do 
./v3_release_from_mass.py --year=$year --variable=$var
done
done
 
for year in 1903 1916
do
for var in PRMSL PRATE TMP2m TMPS UGRD10m VGRD10m observations
do 
./v3_release_from_mass.py --year=$year --variable=$var
done
done 
