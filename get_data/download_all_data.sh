#!/usr/bin/bash

# Run all the data downloads

echo 'CMORPH'
(cd ./CMORPH/satellite && ./get_data_for_period.py  | parallel -j 1)

echo 'CRU'
(cd ./CRU/in_situ && ./get_data_for_period.py | parallel -j 1)

echo 'ERA5'
(cd ERA5 && ./get_data_for_period_ERA5.py | parallel -j 1)

echo 'TWCR'
(cd TWCR && ./get_data_for_period.py | parallel -j 1)
(cd TWCR && ./get_land_mask.py)

echo 'OCADA'
(cd OCADA && ./get_data_for_period.py | parallel -j 1)

echo -n 'GPCC: '
echo -n 'In-situ, '
(cd ./GPCC/in_situ && ./get_data_for_period.py | parallel -j 1)
echo 'Satellite'
(cd ./GPCC/with_satellite && ./get_data_for_period.py | parallel -j 1)

echo -n 'Copernicus: '
echo -n 'Microwave, '
(cd ./Copernicus/satellite_microwave && ./get_data_for_period.py | parallel -j 1)
echo 'Land observations'
(cd ./Copernicus/land_surface_observations && ./get_data_for_period.py | parallel -j 1)

echo -n 'HadCRUT'
(cd HadCRUT && ./get_members.py)

echo -n 'HadISST'
(cd HadISST/v1 && ./get_data.sh)

echo -n 'GPCP'
(cd GPCP/blended && ./get_means.py)

echo -n 'land mask'
(cd land_mask && ./get_land_mask_from_ERA5_land.py)
