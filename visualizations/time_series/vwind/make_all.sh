#!/usr/bin/bash

# Make all the time-series plots
# Uses pre-made pickle files, instead of the normalized tensors if possible
# Delete the .pkl files to force their recreation from the current tensors

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
OP_DIR="$PDIR/visualizations/time_series/vwind"
mkdir -p "$OP_DIR"

# Re-create the processed time-series if needed
for source in TWCR ERA5 GC5
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

# Make a plot at each level of smoothing
$SCRIPT_DIR/plot_series.py --nmonths=1 --ymin=0.3 --ymax=0.6
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.3 --ymax=0.6
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.3 --ymax=0.6
$SCRIPT_DIR/plot_series.py --nmonths=1  --ymin=0.3 --ymax=0.6 --rchoice=area
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.3 --ymax=0.6 --rchoice=area
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.3 --ymax=0.6 --rchoice=area
$SCRIPT_DIR/plot_series.py --nmonths=1  --ymin=0.3 --ymax=0.6 --rchoice=area --mask_file=CRU
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.3 --ymax=0.6 --rchoice=area --mask_file=CRU
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.3 --ymax=0.6 --rchoice=area --mask_file=CRU
$SCRIPT_DIR/plot_series.py --nmonths=1  --ymin=0.3 --ymax=0.6 --rchoice=area --mask_file=Europe
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.3 --ymax=0.6 --rchoice=area --mask_file=Europe
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.3 --ymax=0.6 --rchoice=area --mask_file=Europe
# Frequency-space plots - only use recent data
$SCRIPT_DIR/plot_series.py --spectrum --rchoice=area --nmonths=1 --start_year=1950
$SCRIPT_DIR/plot_series.py --spectrum --rchoice=area --nmonths=1 --start_year=1950 --mask=CRU
$SCRIPT_DIR/plot_series.py --spectrum --rchoice=area --nmonths=1 --start_year=1950 --mask=Europe
