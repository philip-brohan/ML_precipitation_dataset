#!/bin/bash

mkdir -p $SCRATCH/HadISST/v1
wget https://www.metoffice.gov.uk/hadobs/hadisst/data/HadISST_sst.nc.gz -O $SCRATCH/HadISST/v1/HadISST_sst.nc.gz
gunzip $SCRATCH/HadISST/v1/HadISST_sst.nc.gz
