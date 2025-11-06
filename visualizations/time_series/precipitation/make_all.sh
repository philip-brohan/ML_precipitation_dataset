#!/usr/bin/bash

# Make all the time-series plots
# Uses pre-made pickle files, instead of the normalized tensors if possible
# Delete the .pkl files to force their recreation from the current tensors

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
OP_DIR="$PDIR/visualizations/time_series/precipitation"

# Re-create the processed time-series if needed
for source in TWCR ERA5 GPCC_in-situ GPCP CRU
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
$SCRIPT_DIR/plot_series.py --nmonths=1
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.47 --ymax=0.53
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.475 --ymax=0.53
$SCRIPT_DIR/plot_series.py --nmonths=1  --ymin=0.44 --ymax=0.55 --rchoice=area
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.475 --ymax=0.52 --rchoice=area
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.48 --ymax=0.52 --rchoice=area
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.48 --ymax=0.52 --rchoice=area --nosat
$SCRIPT_DIR/plot_series.py --nmonths=1  --ymin=0.44 --ymax=0.55 --rchoice=area --mask_file=CRU
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.475 --ymax=0.52 --rchoice=area --mask_file=CRU
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.48 --ymax=0.535 --rchoice=area --mask_file=CRU
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.48 --ymax=0.53 --rchoice=area --mask_file=CRU --nosat
$SCRIPT_DIR/plot_series.py --nmonths=1  --ymin=0.2 --ymax=0.8 --rchoice=area --mask_file=Europe
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.42 --ymax=0.58 --rchoice=area --mask_file=Europe
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.45 --ymax=0.55 --rchoice=area --mask_file=Europe
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.45 --ymax=0.55 --rchoice=area --mask_file=Europe --nosat

