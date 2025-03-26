#!/bin/bash

# Make all the hourly raw tensors
# Requires downloaded data

(cd TWCR && ../../../azure_tools/azure_run.py --experiment=MLPh --name=hourly_make_raw_tensors_TWCR_t2m --parallel=4 --compute=Philip-E4DS -- make_all_tensors.py --variable=TMP2m )
(cd TWCR && ../../../azure_tools/azure_run.py --experiment=MLPh --name=hourly_make_raw_tensors_TWCR_sst --parallel=4 --compute=Philip-E4DS -- make_all_tensors.py --variable=SST )
(cd TWCR && ../../../azure_tools/azure_run.py --experiment=MLPh --name=hourly_make_raw_tensors_TWCR_mslp --parallel=4 --compute=Philip-E4DS -- make_all_tensors.py --variable=PRMSL )
(cd TWCR && ../../../azure_tools/azure_run.py --experiment=MLPh --name=hourly_make_raw_tensors_TWCR_precip --parallel=4 --compute=Philip-E4DS -- make_all_tensors.py --variable=PRATE )

