#!/bin/bash

# Make normalization constants for all the datasets
# Requires pre-made raw tensors

(cd TWCR_tf_MM && ./make_all_fits.py)

