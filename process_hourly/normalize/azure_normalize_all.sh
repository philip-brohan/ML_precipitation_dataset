#!/bin/bash

# Make normalization constants for all the datasets
# Requires pre-made raw tensors


(cd TWCR_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLPh --name=normalize_TWCR --compute=Philip-D32 --parallel=32 -- make_all_fits.py)

