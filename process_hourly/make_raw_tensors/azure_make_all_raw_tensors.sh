#!/bin/bash

# Make all the raw tensors
# Requires downloaded data

(cd CRU/in_situ && ../../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_CRU --parallel=4 --compute=cpu-cluster -- make_all_tensors.py )

(cd ERA5 && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_ERA5_t2m --parallel=31 --compute=multicore-32 -- make_all_tensors.py --variable=2m_temperature )
(cd ERA5 && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_ERA5_sst --parallel=31 --compute=multicore-32 -- make_all_tensors.py --variable=sea_surface_temperature )
(cd ERA5 && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_ERA5_mslp --parallel=31 --compute=multicore-32 -- make_all_tensors.py --variable=mean_sea_level_pressure )
(cd ERA5 && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_ERA5_precip --parallel=31 --compute=multicore-32 -- make_all_tensors.py --variable=total_precipitation )

(cd TWCR && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_TWCR_t2m --parallel=31 --compute=multicore-32 -- make_all_tensors.py --variable=TMP2m )
(cd TWCR && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_TWCR_sst --parallel=31 --compute=multicore-32 -- make_all_tensors.py --variable=SST )
(cd TWCR && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_TWCR_mslp --parallel=31 --compute=multicore-32 -- make_all_tensors.py --variable=PRMSL )
(cd TWCR && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_TWCR_precip --parallel=31 --compute=multicore-32 -- make_all_tensors.py --variable=PRATE )

(cd GPCC/in_situ && ../../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_GPCC --parallel=4 --compute=cpu-cluster -- make_all_tensors.py )

(cd HadCRUT && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_HadCRUT --parallel=16 --compute=multicore-32 -- make_all_tensors.py)

(cd HadISST && ../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_HadISST --parallel=4 --compute=cpu-cluster -- make_all_tensors.py )

(cd GPCP/blended && ../../../azure_tools/azure_run.py --experiment=MLP --name=make_raw_tensors_GPCP --parallel=4 --compute=cpu-cluster -- make_all_tensors.py )
