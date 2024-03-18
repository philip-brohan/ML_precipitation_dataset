#!/usr/bin/bash

# Make all the time-series plots
# Requires pre-made normalized tensors.

(cd ./temperature && ./make_all.sh)

(cd ./pressure && ./make_all.sh)

(cd ./precipitation && ./make_all.sh)