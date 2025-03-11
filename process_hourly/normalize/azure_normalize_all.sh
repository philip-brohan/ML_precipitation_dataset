#!/bin/bash

# Make normalization constants for all the datasets
# Requires pre-made raw tensors


(cd TWCR_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLP --name=normalize_TWCR --compute=multicore-32 --parallel=4 -- make_all_fits.py)

