#!/bin/bash

# Upload all the data to Azure

echo 'CMORPH'
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/CMORPH --remote=/default/MLP/CMORPH)

echo 'CRU'
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/CRU --remote=/default/MLP/CRU)

echo 'ERA5'
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/ERA5 --remote=/default/MLP/ERA5)

echo 'TWCR'
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/20CR --remote=/default/MLP/20CR)

echo -n 'GPCC: '
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/GPCC/in-situ --remote=/default/MLP/GPCC/in-situ)

echo -n 'Copernicus: '
echo -n 'Microwave, '
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/Copernicus/satellite_microwave --remote=/default/MLP/Copernicus/satellite_microwave)
echo 'Land observations'
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/Copernicus/land_surface_observations --remote=/default/MLP/Copernicus/land_surface_observations)

echo -n 'HadCRUT'
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/HadCRUT --remote=/default/MLP/HadCRUT)


echo -n 'HadISST'
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/HadISST/v1 --remote=/default/MLP/HadISST/v1)

echo -n 'GPCP'
(../azure_tools/azure_upload.py --local=/data/scratch/philip.brohan/MLP/GPCP --remote=/default/MLP/GPCP)

