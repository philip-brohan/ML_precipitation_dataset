#!/usr/bin/bash

# Make all the stripes plots
# Requires pre-made normalized tensors.

(cd ./CRU && ./make_all.sh)

(cd ERA5 && ./make_all.sh)

(cd TWCR && ./make_all.sh)

(cd ./GPCC/in_situ && ./make_all.sh)
(cd ./GPCC/blended && ./make_all.sh)

(cd HadCRUT && ./make_all.sh)

(cd HadISST && ./make_all.sh)

(cd GPCP && ./make_all.sh)
