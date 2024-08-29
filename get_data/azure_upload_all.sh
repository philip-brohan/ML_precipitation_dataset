#!/bin/bash

# Upload all the data to Azure

echo 'CMORPH'
(../azure_tools/azure_upload.py --local=/scratch/hadpb/CMORPH --remote=SCRATCH/CMORPH)

echo 'CRU'
(../azure_tools/azure_upload.py --local=/scratch/hadpb/CRU --remote=SCRATCH/CRU)

echo 'ERA5'
(../azure_tools/azure_upload.py --local=/scratch/hadpb/ERA5 --remote=SCRATCH/ERA5)

echo 'TWCR'
(../azure_tools/azure_upload.py --local=/scratch/hadpb/20CR --remote=SCRATCH/20CR)

echo -n 'GPCC: '
(../azure_tools/azure_upload.py --local=/scratch/hadpb/GPCC/in-situ --remote=SCRATCH/GPCC/in-situ)

echo -n 'Copernicus: '
echo -n 'Microwave, '
(../azure_tools/azure_upload.py --local=/scratch/hadpb/Copernicus/satellite_microwave --remote=SCRATCH/Copernicus/satellite_microwave)
echo 'Land observations'
(../azure_tools/azure_upload.py --local=/scratch/hadpb/Copernicus/land_surface_observations --remote=SCRATCH/Copernicus/land_surface_observations)

echo -n 'HadCRUT'
(../azure_tools/azure_upload.py --local=/scratch/hadpb/HadCRUT --remote=SCRATCH/HadCRUT)


echo -n 'HadISST'
(../azure_tools/azure_upload.py --local=/scratch/hadpb/HadISST/v1 --remote=SCRATCH/HadISST/v1)

echo -n 'GPCP'
(../azure_tools/azure_upload.py --local=/scratch/hadpb/GPCP --remote=SCRATCH/GPCP)

