#!/usr/bin/bash

# Make normalisation constants for all the datasets

(cd ./CRU_tf_MM && ./make_all_fits.py)

(cd ERA5_tf_MM && ./make_all_fits.py)

(cd TWCR_tf_MM && ./make_all_fits.py)

(cd ./GPCC_tf_MM/in_situ && ./make_all_fits.py)
(cd ./GPCC_tf_MM/blended && ./make_all_fits.py)

(cd HadCRUT_tf_MM && ./make_all_fits.py)

#(cd HadISST_tf_MM && ./make_all_fits.py)

(cd GPCP_tf_MM && ./make_all_fits.py)
