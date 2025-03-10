#!/bin/bash

# Update the raw tensors metadata

(cd CRU/in_situ && ../../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_CRU --compute=cpu-cluster -- update_tensor_metadata.py )

(cd ERA5 && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_ERA5_t2m --compute=cpu-cluster -- update_tensor_metadata.py --variable=2m_temperature )
(cd ERA5 && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_ERA5_sst --compute=cpu-cluster -- update_tensor_metadata.py --variable=sea_surface_temperature )
(cd ERA5 && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_ERA5_mslp --compute=cpu-cluster -- update_tensor_metadata.py --variable=mean_sea_level_pressure )
(cd ERA5 && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_ERA5_precip --compute=cpu-cluster -- update_tensor_metadata.py --variable=total_precipitation )

(cd TWCR && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_TWCR_t2m --compute=cpu-cluster -- update_tensor_metadata.py --variable=TMP2m )
(cd TWCR && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_TWCR_sst --compute=cpu-cluster -- update_tensor_metadata.py --variable=SST )
(cd TWCR && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_TWCR_mslp --compute=cpu-cluster -- update_tensor_metadata.py --variable=PRMSL )
(cd TWCR && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_TWCR_precip --compute=cpu-cluster -- update_tensor_metadata.py --variable=PRATE )

(cd GPCC/in_situ && ../../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_GPCC --compute=cpu-cluster -- update_tensor_metadata.py )

(cd HadCRUT && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_HadCRUT --compute=cpu-cluster -- update_tensor_metadata.py)

(cd HadISST && ../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_HadISST --compute=cpu-cluster -- update_tensor_metadata.py )

(cd GPCP/blended && ../../../azure_tools/azure_run.py --experiment=MLP --name=raw_tensors_metadata_GPCP --compute=cpu-cluster -- update_tensor_metadata.py )
