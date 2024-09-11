#!/bin/bash

# Make normalized tensors for all the datasets
# Requires pre-made raw tensors and normalization factors

(cd ./CRU_tf_MM/ && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_CRU --compute=cpu-cluster -- make_all_tensors.py)

(cd ERA5_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_ERA5_t2m --compute=cpu-cluster -- make_all_tensors.py --variable=2m_temperature)
(cd ERA5_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_ERA5_sst --compute=cpu-cluster -- make_all_tensors.py --variable=sea_surface_temperature)
(cd ERA5_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_ERA5_mslp --compute=cpu-cluster -- make_all_tensors.py --variable=mean_sea_level_pressure)
(cd ERA5_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_ERA5_precip --compute=cpu-cluster -- make_all_tensors.py --variable=total_precipitation)

# Use multicore-32 for TWCR because it needs more RAM
(cd TWCR_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_TWCR_t2m --compute=multicore-32 -- make_all_tensors.py --variable=TMP2m)
(cd TWCR_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_TWCR_sst --compute=multicore-32 -- make_all_tensors.py --variable=SST)
(cd TWCR_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_TWCR_mslp --compute=multicore-32 -- make_all_tensors.py --variable=PRMSL)
(cd TWCR_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_TWCR_precip --compute=multicore-32 -- make_all_tensors.py --variable=PRATE)

(cd ./GPCC_tf_MM/in_situ && ../../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_GPCC --compute=cpu-cluster -- make_all_tensors.py)

(cd HadCRUT_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_HadCRUT --compute=multicore-32 -- make_all_tensors.py)

(cd HadISST_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_HadISST --compute=cpu-cluster -- make_all_tensors.py)

(cd GPCP_tf_MM && ../../azure_tools/azure_run.py --experiment=MLP --name=make_normalized_GPCP --compute=cpu-cluster -- make_all_tensors.py)
