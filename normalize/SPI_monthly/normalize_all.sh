#!/bin/bash

# Make normalization constants for all the datasets
# Requires pre-made raw tensors

(cd ./CRU_tf_MM/ && ./make_all_fits.py)

(cd ERA5_tf_MM && ./make_all_fits.py)

(cd TWCR_tf_MM && ./make_all_fits.py)

(cd ./GPCC_tf_MM/in_situ && ./make_all_fits.py)

(cd HadCRUT_tf_MM && ./make_all_fits.py)

(cd HadISST_tf_MM && ./make_all_fits.py)

(cd GPCP_tf_MM && ./make_all_fits.py)
