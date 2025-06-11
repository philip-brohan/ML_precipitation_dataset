#!/bin/bash

# Download the trained weights and training logs from azure

../../azure_tools/azure_download.py --local=$PDIR/ML_models/Default --remote=/default/MLP/ML_models/Default
