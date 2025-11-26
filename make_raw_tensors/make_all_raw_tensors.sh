#!/bin/bash

# Make all the raw tensors
# Requires downloaded data

(cd ./CRU/in_situ && ./make_all_tensors.py)

(cd ERA5 && ./make_all_tensors.py --variable=2m_temperature)
(cd ERA5 && ./make_all_tensors.py --variable=sea_surface_temperature)
(cd ERA5 && ./make_all_tensors.py --variable=mean_sea_level_pressure)
(cd ERA5 && ./make_all_tensors.py --variable=total_precipitation)
(cd ERA5 && ./make_all_tensors.py --variable=10m_u_component_of_wind)
(cd ERA5 && ./make_all_tensors.py --variable=10m_u_component_of_wind)
(cd ERA5 && ./make_all_tensors.py --variable=2m_dewpoint_temperature)
(cd ERA5 && ./make_all_tensors.py --variable=2m_relative_humidity)


(cd GC5-Central && ./make_all_tensors.py --run=dl339 --variable=prate)
(cd GC5-Central && ./make_all_tensors.py --run=dl340 --variable=prate)
(cd GC5-Central && ./make_all_tensors.py --run=dl341 --variable=prate)
(cd GC5-Central && ./make_all_tensors.py --run=dl339 --variable=t2m)
(cd GC5-Central && ./make_all_tensors.py --run=dl340 --variable=t2m)
(cd GC5-Central && ./make_all_tensors.py --run=dl341 --variable=t2m)
(cd GC5-Central && ./make_all_tensors.py --run=dl339 --variable=prmsl)
(cd GC5-Central && ./make_all_tensors.py --run=dl340 --variable=prmsl)
(cd GC5-Central && ./make_all_tensors.py --run=dl341 --variable=prmsl)

(cd TWCR && ./make_all_tensors.py --variable=TMP2m)
(cd TWCR && ./make_all_tensors.py --variable=SST)
(cd TWCR && ./make_all_tensors.py --variable=PRMSL)
(cd TWCR && ./make_all_tensors.py --variable=PRATE)
(cd TWCR && ./make_all_tensors.py --variable=UGRD10m)
(cd TWCR && ./make_all_tensors.py --variable=VGRD10m)
(cd TWCR && ./make_all_tensors.py --variable=RH2m)

(cd ./GPCC/in_situ && ./make_all_tensors.py)

(cd HadCRUT && ./make_all_tensors.py)

(cd HadISST && ./make_all_tensors.py)

(cd GPCP/blended && ./make_all_tensors.py)
