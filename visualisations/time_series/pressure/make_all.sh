#!/usr/bin/bash

# Make all the time-series plots
# Uses pre-made pickle files, instead of the normalised tensors if possible
# Delete the .pkl files to force their recreation from the current tensors

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Re-create the processed time-series if needed
for source in TWCR ERA5
do
    if ! [ -f "$SCRIPT_DIR/$source.pkl" ]; then
        $SCRIPT_DIR/get_series.py --source=$source
    fi
done

# Make a plot at each level of smoothing
$SCRIPT_DIR/plot_series.py --nmonths=1 --ymin=0.35 --ymax=0.6
$SCRIPT_DIR/plot_series.py --nmonths=13 --ymin=0.35 --ymax=0.6
$SCRIPT_DIR/plot_series.py --nmonths=39 --ymin=0.35 --ymax=0.6

