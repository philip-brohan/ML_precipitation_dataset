#!/bin/bash

mkdir -p $PDIR/HadISST/v1
wget https://www.metoffice.gov.uk/hadobs/hadisst/data/HadISST_sst.nc.gz -O $PDIR/HadISST/v1/HadISST_sst.nc.gz
gunzip $PDIR/HadISST/v1/HadISST_sst.nc.gz
