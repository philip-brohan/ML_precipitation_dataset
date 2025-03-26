#!/bin/bash

# Update the hourly raw tensors metadata


(cd TWCR && ../../../azure_tools/azure_run.py --experiment=MLPh --name=hourly_raw_tensors_metadata_TWCR_t2m --compute=Philip-E4DS -- update_tensor_metadata.py --variable=TMP2m )
(cd TWCR && ../../../azure_tools/azure_run.py --experiment=MLPh --name=hourly_raw_tensors_metadata_TWCR_sst --compute=Philip-E4DS -- update_tensor_metadata.py --variable=SST )
(cd TWCR && ../../../azure_tools/azure_run.py --experiment=MLPh --name=hourly_raw_tensors_metadata_TWCR_mslp --compute=Philip-E4DS -- update_tensor_metadata.py --variable=PRMSL )
(cd TWCR && ../../../azure_tools/azure_run.py --experiment=MLPh --name=hourly_raw_tensors_metadata_TWCR_precip --compute=Philip-E4DS -- update_tensor_metadata.py --variable=PRATE )

