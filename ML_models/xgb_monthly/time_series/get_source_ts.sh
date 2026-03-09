#!/usr/bin/bash

# Make the time-seies from all the source datasets

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for source in TWCR ERA5 GPCC_in-situ GPCP CRU GC5
do
    if ! [ -f "$OP_DIR/None_None_$source.pkl" ]; then
        $SCRIPT_DIR/get_series.py --source=$source
    fi
    if ! [ -f "$OP_DIR/None_area_$source.pkl" ]; then
        $SCRIPT_DIR/get_series.py --source=$source --rchoice=area
    fi
    if ! [ -f "$OP_DIR/CRU_area_$source.pkl" ]; then
        $SCRIPT_DIR/get_series.py --source=$source --rchoice=area --mask_file=CRU
    fi
    if ! [ -f "$OP_DIR/Europe_area_$source.pkl" ]; then
        $SCRIPT_DIR/get_series.py --source=$source --rchoice=area --mask_file=Europe
    fi
done
