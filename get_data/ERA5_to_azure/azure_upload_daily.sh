#!/bin/bash

# Upload selected daily data to azure

../../azure_tools/azure_upload.py --local=/project/applied/Data/OBS_ERA5/daily/tas --storage_account=obsera5 --file_system=uploaded --remote=daily/tas
../../azure_tools/azure_upload.py --local=/project/applied/Data/OBS_ERA5/daily/mslp --storage_account=obsera5 --file_system=uploaded --remote=daily/mslp
../../azure_tools/azure_upload.py --local=/project/applied/Data/OBS_ERA5/daily/pr --storage_account=obsera5 --file_system=uploaded --remote=daily/pr



