#!/usr/bin/bash

# Make all the raw tensors
# Requires downloaded data

(cd ./CRU/in_situ && ./make_all_tensors.py)

(cd ERA5 && ./make_all_tensors.py --variable=2m_temperature)
(cd ERA5 && ./make_all_tensors.py --variable=sea_surface_temperature)
(cd ERA5 && ./make_all_tensors.py --variable=mean_sea_level_pressure)
(cd ERA5 && ./make_all_tensors.py --variable=total_precipitation)

(cd TWCR && ./make_all_tensors.py --variable=TMP2m)
(cd TWCR && ./make_all_tensors.py --variable=SST)
(cd TWCR && ./make_all_tensors.py --variable=PRMSL)
(cd TWCR && ./make_all_tensors.py --variable=PRATE)

(cd OCADA && ./make_all_tensors.py --variable=ta)
(cd OCADA && ./make_all_tensors.py --variable=slp)
(cd OCADA && ./make_all_tensors.py --variable=precipi)

(cd ./GPCC/in_situ && ./make_all_tensors.py)
(cd ./GPCC/blended && ./make_all_tensors.py)

(cd HadCRUT && ./make_all_tensors.py)

(cd HadISST && ./make_all_tensors.py)

(cd GPCP/blended && ./make_all_tensors.py)
