#!/bin/bash

# Add metadata to the raw tensor zarr files
# Requires raw tensors

(cd ./CRU/in_situ && ./update_tensor_metadata.py)

(cd ERA5 && ./update_tensor_metadata.py --variable=2m_temperature)
(cd ERA5 && ./update_tensor_metadata.py --variable=sea_surface_temperature)
(cd ERA5 && ./update_tensor_metadata.py --variable=mean_sea_level_pressure)
(cd ERA5 && ./update_tensor_metadata.py --variable=total_precipitation)

(cd TWCR && ./update_tensor_metadata.py --variable=TMP2m)
(cd TWCR && ./update_tensor_metadata.py --variable=SST)
(cd TWCR && ./update_tensor_metadata.py --variable=PRMSL)
(cd TWCR && ./update_tensor_metadata.py --variable=PRATE)

(cd GC5-Central && ./update_tensor_metadata --run=dl339 --variable=prate)
(cd GC5-Central && ./update_tensor_metadata --run=dl340 --variable=prate)
(cd GC5-Central && ./update_tensor_metadata --run=dl341 --variable=prate)
(cd GC5-Central && ./update_tensor_metadata --run=dl339 --variable=t2m)
(cd GC5-Central && ./update_tensor_metadata --run=dl340 --variable=t2m)
(cd GC5-Central && ./update_tensor_metadata --run=dl341 --variable=t2m)
(cd GC5-Central && ./update_tensor_metadata --run=dl339 --variable=prmsl)
(cd GC5-Central && ./update_tensor_metadata --run=dl340 --variable=prmsl)
(cd GC5-Central && ./update_tensor_metadata --run=dl341 --variable=prmsl)

(cd ./GPCC/in_situ && ./update_tensor_metadata.py)

(cd HadCRUT && ./update_tensor_metadata.py)

(cd HadISST && ./update_tensor_metadata.py)

(cd GPCP/blended && ./update_tensor_metadata.py)
