#!/usr/bin/bash

# Make all the time-series plots
# Uses pre-made pickle files, instead of the normalized tensors if possible
# Delete the .pkl files to force their recreation from the current tensors

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
OP_DIR="$PDIR/visualizations/time_series/temperature"
mkdir -p "$OP_DIR"

# Re-create the processed time-series if needed
for source in TWCR_sst TWCR_t2m ERA5_sst ERA5_t2m HadCRUT HadISST GC5
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
$SCRIPT_DIR/plot_series.py --nmonths=1 --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.2 --ymax=0.75 --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.2 --ymax=0.7 --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=1 --rchoice=area --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.2 --ymax=0.75 --rchoice=area --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.3 --ymax=0.7 --rchoice=area --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=1  --ymin=0.2 --ymax=0.75 --rchoice=area --mask_file=CRU --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.2 --ymax=0.75 --rchoice=area --mask_file=CRU --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.2 --ymax=0.75 --rchoice=area --mask_file=CRU --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=1  --ymin=0.2 --ymax=0.75 --rchoice=area --mask_file=Europe --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.2 --ymax=0.75 --rchoice=area --mask_file=Europe --hscale=0.6
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.2 --ymax=0.75 --rchoice=area --mask_file=Europe --hscale=0.6
# Frequency-space plots - only use recent data
$SCRIPT_DIR/plot_series.py --spectrum --rchoice=area --nmonths=1 --start_year=1950 --hscale=0.6
$SCRIPT_DIR/plot_series.py --spectrum --rchoice=area --nmonths=1 --start_year=1950 --mask=CRU --hscale=0.6
$SCRIPT_DIR/plot_series.py --spectrum --rchoice=area --nmonths=1 --start_year=1950 --mask=Europe --hscale=0.6

