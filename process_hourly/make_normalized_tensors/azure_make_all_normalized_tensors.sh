#!/bin/bash

# Make normalized tensors for all the datasets
# Requires pre-made raw tensors and normalization factors

# Use Philip-D32 for TWCR because it needs more RAM
(cd TWCR_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLPh --name=make_normalized_TWCR_t2m --compute=Philip-D32 -- make_all_tensors.py --variable=TMP2m)
(cd TWCR_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLPh --name=make_normalized_TWCR_sst --compute=Philip-D32 -- make_all_tensors.py --variable=SST)
(cd TWCR_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLPh --name=make_normalized_TWCR_mslp --compute=Philip-D32 -- make_all_tensors.py --variable=PRMSL)
(cd TWCR_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLPh --name=make_normalized_TWCR_precip --compute=Philip-D32 -- make_all_tensors.py --variable=PRATE)

