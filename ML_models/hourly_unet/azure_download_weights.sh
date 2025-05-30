#!/bin/bash

# Download the trained weights and training logs from azure

../../azure_tools/azure_download.py --local=$SCRATCH/DCVAE-Climate/Default --remote=SCRATCH/DCVAE-Climate/Default
