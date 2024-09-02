#!/bin/bash

# Make normalization constants for all the datasets
# Requires pre-made raw tensors

(cd ./CRU_tf_MM/ && ../../../azure_tools/azure_run.py --experiment=MLP --name=normalize_CRU --compute=cpu-cluster --parallel=1 -- make_all_fits.py)

(cd ERA5_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLP --name=normalize_ERA5 --compute=multicore-32 --parallel=4 -- make_all_fits.py)

(cd TWCR_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLP --name=normalize_TWCR --compute=multicore-32 --parallel=4 -- make_all_fits.py)

(cd ./GPCC_tf_MM/in_situ && ../../../../azure_tools/azure_run.py --experiment=MLP --name=normalize_GPCC --compute=cpu-cluster --parallel=1 -- make_all_fits.py)

(cd HadCRUT_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLP --name=normalize_HadCRUT --compute=cpu-cluster --parallel=1 -- make_all_fits.py)

(cd HadISST_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLP --name=normalize_HadISST --compute=cpu-cluster --parallel=1 -- make_all_fits.py)

(cd GPCP_tf_MM && ../../../azure_tools/azure_run.py --experiment=MLP --name=normalize_GPCP --compute=cpu-cluster --parallel=1 -- make_all_fits.py)
