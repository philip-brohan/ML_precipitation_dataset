#!/bin/bash

# Make all the normalized tensors
# Requires pre-made normalization parameters.

(cd ./CRU_tf_MM && ./make_all_tensors.py)

(cd ERA5_tf_MM && ./make_all_tensors.py --variable=2m_temperature)
(cd ERA5_tf_MM && ./make_all_tensors.py --variable=sea_surface_temperature)
(cd ERA5_tf_MM && ./make_all_tensors.py --variable=mean_sea_level_pressure)
(cd ERA5_tf_MM && ./make_all_tensors.py --variable=total_precipitation)

(cd TWCR_tf_MM && ./make_all_tensors.py --variable=TMP2m)
(cd TWCR_tf_MM && ./make_all_tensors.py --variable=SST)
(cd TWCR_tf_MM && ./make_all_tensors.py --variable=PRMSL)
(cd TWCR_tf_MM && ./make_all_tensors.py --variable=PRATE)

(cd ./GPCC_tf_MM/in_situ && ./make_all_tensors.py)

(cd HadCRUT_tf_MM && ./make_all_tensors.py)

(cd HadISST_tf_MM && ./make_all_tensors.py)

(cd GPCP_tf_MM && ./make_all_tensors.py)
