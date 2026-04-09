#!/usr/bin/env python

# Prepare data, train a model, and make validation plots.

import os
import sys

import argparse
import subprocess


def run_cmd(cmd):
    try:
        # use bash so complex commands/pipes work the same as before
        subprocess.run(cmd, shell=True, check=True, executable="/bin/bash")
    except KeyboardInterrupt:
        print("Interrupted by user, exiting.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Command failed ({e.returncode}): {cmd}")
        sys.exit(e.returncode)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--samples",
    type=int,
    required=False,
    default=None,
)
parser.add_argument(
    "--member_idx", help="Member index (0-9)", type=int, required=False, default=None
)
parser.add_argument("--no_pressure", action="store_true")
parser.add_argument("--no_pressure_sd", action="store_true")
parser.add_argument("--no_temperature", action="store_true")
parser.add_argument("--no_uwind", action="store_true")
parser.add_argument("--no_vwind", action="store_true")
parser.add_argument("--no_humidity", action="store_true")
parser.add_argument("--fix_month", type=int, required=False, default=None)
parser.add_argument("--fix_lat", type=int, required=False, default=None)
parser.add_argument("--fix_lon", type=int, required=False, default=None)
parser.add_argument("--lat_offset", type=int, required=False, default=None)
parser.add_argument("--lon_offset", type=int, required=False, default=None)

parser.add_argument(
    "--start_year",
    type=int,
    required=True,
)
parser.add_argument(
    "--end_year",
    type=int,
    required=True,
)
parser.add_argument(
    "--training_start_year",
    type=int,
    required=True,
)
parser.add_argument(
    "--training_end_year",
    type=int,
    required=True,
)
parser.add_argument(
    "--label",  # name for this model
    type=str,
    required=True,
    default=None,
)
parser.add_argument(
    "--source",
    type=str,  # 'TWCR','ERA5', or 'GC5'
    required=True,
    default=None,
)
parser.add_argument(
    "--target",
    type=str,  # 'TWCR','ERA5','GC5','GPCC','CRU','GPCP'
    required=True,
    default=None,
)
args = parser.parse_args()

if args.target is None:
    args.target = args.source

# Make the directory to store everything for this model
opdir = "%s/ML_models/xgb_monthly/%s" % (os.getenv("PDIR"), args.label)
if not os.path.exists(opdir):
    os.makedirs(opdir)

# Make the training data if it does not already exist
if not os.path.exists("%s/%s_train.dt" % (opdir, args.source)):
    # Prepare the training data
    cmd = "srun --time=60 --mem=32G ./make_dmatrix.py --opdir=%s " % (opdir,)
    if args.no_pressure:
        cmd += "--no_pressure "
    if args.no_pressure_sd:
        cmd += "--no_pressure_sd "
    if args.no_temperature:
        cmd += "--no_temperature "
    if args.no_uwind:
        cmd += "--no_uwind "
    if args.no_vwind:
        cmd += "--no_vwind "
    if args.no_humidity:
        cmd += "--no_humidity "
    if args.fix_month is not None:
        cmd += "--fix_month %s " % (str(args.fix_month))
    if args.fix_lat is not None:
        cmd += "--fix_lat %s " % (str(args.fix_lat))
    if args.lat_offset is not None:
        cmd += "--lat_offset %d " % (args.lat_offset)
    if args.fix_lon is not None:
        cmd += "--fix_lon %s " % (str(args.fix_lon))
    if args.lon_offset is not None:
        cmd += "--lon_offset %d " % (args.lon_offset)
    if args.samples is not None:
        cmd += "--samples %d " % (args.samples)
    if args.member_idx is not None:
        cmd += "--member_idx %s " % (args.member_idx)
    cmd += "--start_year %s --end_year %s " % (
        str(args.training_start_year),
        str(args.training_end_year),
    )
    cmd += "--label train "
    cmd += "--source %s " % (args.source)
    cmd += "--target %s " % (args.target)
    print(cmd)
    run_cmd(cmd)
else:
    print("Training data already made")

# Make the test data if it does not already exist
if not os.path.exists("%s/%s_test.dt" % (opdir, args.source)):
    # Prepare the training data
    cmd = "srun --time=60 --mem=32G ./make_dmatrix.py --opdir=%s " % (opdir,)
    if args.no_pressure:
        cmd += "--no_pressure "
    if args.no_pressure_sd:
        cmd += "--no_pressure_sd "
    if args.no_temperature:
        cmd += "--no_temperature "
    if args.no_uwind:
        cmd += "--no_uwind "
    if args.no_vwind:
        cmd += "--no_vwind "
    if args.no_humidity:
        cmd += "--no_humidity "
    if args.fix_month is not None:
        cmd += "--fix_month %s " % (str(args.fix_month))
    if args.fix_lat is not None:
        cmd += "--fix_lat %s " % (str(args.fix_lat))
    if args.lat_offset is not None:
        cmd += "--lat_offset %d " % (args.lat_offset)
    if args.fix_lon is not None:
        cmd += "--fix_lon %s " % (str(args.fix_lon))
    if args.lon_offset is not None:
        cmd += "--lon_offset %d " % (args.lon_offset)
    if args.samples is not None:
        cmd += "--samples %d " % (args.samples)
    if args.member_idx is not None:
        cmd += "--member_idx %s " % (args.member_idx)
    cmd += "--start_year %s --end_year %s " % (str(args.start_year), str(args.end_year))
    cmd += "--label test "
    cmd += "--source %s " % (args.source)
    cmd += "--target %s " % (args.target)
    print(cmd)
    run_cmd(cmd)
else:
    print("Test data already made")

# Train the model if not already done
if not os.path.exists("%s/%s.ubj" % (opdir, args.source)):
    cmd = "srun --time=90 --mem=32G --cpus-per-task=4 ./fit_model.py "
    cmd += "--mlabel=%s/%s " % (
        args.label,
        args.source,
    )
    cmd += "--label %s/%s_train " % (args.label, args.source)
    cmd += "--test_label %s/%s_test " % (args.label, args.source)
    cmd += "> %s/train.log " % (opdir,)
    print(cmd)
    run_cmd(cmd)
else:
    print("Model already trained")
# Make validation plots
# Make test:train validation plot
if not os.path.exists("%s/test_train.webp" % (opdir,)):
    cmd = "srun --time=30 --mem=32G --cpus-per-task=4 ./validate_2.py "
    cmd += "--mlabel1 %s/%s " % (args.label, args.source)
    cmd += "--label1 %s/%s_train " % (args.label, args.source)
    cmd += "--mlabel2 %s/%s " % (args.label, args.source)
    cmd += "--label2 %s/%s_test " % (args.label, args.source)
    cmd += "--out %s/test_train.webp " % (opdir,)
    print(cmd)
    run_cmd(cmd)
else:
    print("Test:train validation plot already made")

# Make monthly validation plot
if not os.path.exists("%s/monthly.webp" % (opdir,)):
    cmd = "srun --time=25 --mem=32G --cpus-per-task=2 ./validate_month.py "
    cmd += "--mlabel %s/%s " % (args.label, args.source)
    cmd += "--source %s " % (args.source,)
    cmd += "--target %s " % (args.target)
    cmd += "--out %s/monthly.webp " % (opdir,)
    if args.no_pressure:
        cmd += "--no_pressure "
    if args.no_pressure_sd:
        cmd += "--no_pressure_sd "
    if args.no_temperature:
        cmd += "--no_temperature "
    if args.no_uwind:
        cmd += "--no_uwind "
    if args.no_vwind:
        cmd += "--no_vwind "
    if args.no_humidity:
        cmd += "--no_humidity "
    if args.fix_month is not None:
        cmd += "--fix_month %s " % (str(args.fix_month))
    if args.lat_offset is not None:
        cmd += "--lat_offset %d " % (args.lat_offset)
    if args.fix_lat is not None:
        cmd += "--fix_lat %s " % (str(args.fix_lat))
    if args.lon_offset is not None:
        cmd += "--lon_offset %d " % (args.lat_offset)
    if args.fix_lon is not None:
        cmd += "--fix_lon %s " % (str(args.fix_lon))
    if args.member_idx is not None:
        cmd += "--member_idx %s " % (args.member_idx)
    print(cmd)
    run_cmd(cmd)
else:
    print("Monthly validation plot already made")

# Make model prediction for each month
if not os.path.exists("%s/ts_validation/model_zarr/.zattrs" % (opdir,)):
    cmd = "./validate_time_series_parallel.py "
    cmd += "--mlabel %s/%s " % (args.label, args.source)
    cmd += "--label %s " % (args.label)
    cmd += "--source %s " % (args.source,)
    cmd += "--target %s " % (args.target)
    if args.no_pressure:
        cmd += "--no_pressure "
    if args.no_pressure_sd:
        cmd += "--no_pressure_sd "
    if args.no_temperature:
        cmd += "--no_temperature "
    if args.no_uwind:
        cmd += "--no_uwind "
    if args.no_vwind:
        cmd += "--no_vwind "
    if args.no_humidity:
        cmd += "--no_humidity "
    if args.fix_month is not None:
        cmd += "--fix_month %s " % (str(args.fix_month))
    if args.lat_offset is not None:
        cmd += "--lat_offset %d " % (args.lat_offset)
    if args.fix_lat is not None:
        cmd += "--fix_lat %s " % (str(args.fix_lat))
    if args.lon_offset is not None:
        cmd += "--lon_offset %d " % (args.lat_offset)
    if args.fix_lon is not None:
        cmd += "--fix_lon %s " % (str(args.fix_lon))
    if args.member_idx is not None:
        cmd += "--member_idx %s " % (args.member_idx)
    cmd += "--start_year %s --end_year %s " % (str(args.start_year), str(args.end_year))
    # run the output of this command in parallel on spice
    cmd += " | spice_parallel --time=30 --ntasks=4 --mem=32000 --maxjobs=200 "
    print(cmd)
    run_cmd(cmd)
    cmd = (
        "srun --time=25 --mem=32G --cpus-per-task=4 ./update_tensor_metadata.py --label %s "
        % (args.label)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series validation data already made")

# Make set of stripes plots
if not os.path.exists("%s/stripes/model_stripes_sample_none.webp" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=16G --cpus-per-task=4 ./stripes/stripes.py --label=%s --convolve=none --startyear=%04d --endyear=%04d"
        % (args.label, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Stripes sample none already made")
if not os.path.exists("%s/stripes/model_stripes_sample_11x13.webp" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=16G --cpus-per-task=4 ./stripes/stripes.py --label=%s --convolve=11x13 --startyear=%04d --endyear=%04d  --vmin=0.25 --vmax=0.75"
        % (args.label, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Stripes sample 11x13 already made")
if not os.path.exists("%s/stripes/3_stripes_sample_none.webp" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=16G --cpus-per-task=4 ./stripes/stripes_triple.py --label=%s --target=%s --convolve=none --startyear=%04d --endyear=%04d"
        % (args.label, args.target, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Stripes triple none already made")
if not os.path.exists("%s/stripes/3_stripes_sample_11x13.webp" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=16G --cpus-per-task=4 ./stripes/stripes_triple.py --label=%s --target=%s --convolve=11x13 --startyear=%04d --endyear=%04d  --vmin=0.25 --vmax=0.75"
        % (args.label, args.target, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Stripes triple 11x13 already made")

# Make target time-series
if not os.path.exists(
    "%s/../sources/%s/None_area_%s.pkl" % (opdir, args.target, args.target)
):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series.py --source=%s  --rchoice=area"
        % (args.target,)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series None_area_%s already made" % (args.target,))
if not os.path.exists(
    "%s/../sources/%s/CRU_area_%s.pkl" % (opdir, args.target, args.target)
):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series.py --source=%s  --rchoice=area --mask_file=CRU"
        % (args.target,)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series CRU_area_%s already made" % (args.target,))
if not os.path.exists(
    "%s/../sources/%s/Europe_area_%s.pkl" % (opdir, args.target, args.target)
):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series.py --source=%s  --rchoice=area --mask_file=Europe"
        % (args.target,)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series Europe_area_%s already made" % (args.target,))

# Make model time-series
if not os.path.exists("%s/series/None_area_None.pkl" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series.py --label=%s  --rchoice=area"
        % (args.label,)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series None_area_None already made")
if not os.path.exists("%s/series/CRU_area_None.pkl" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series.py --label=%s  --rchoice=area --mask_file=CRU"
        % (args.label,)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series CRU_area_None already made")
if not os.path.exists("%s/series/Europe_area_None.pkl" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series.py --label=%s  --rchoice=area --mask_file=Europe"
        % (args.label,)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series Europe_area_None already made")

# Make time-series plots
for nmonths in [1, 13, 39]:
    for mask in [None, "CRU", "Europe"]:
        if not os.path.exists("%s/series/%s_area_%03d.webp" % (opdir, mask, nmonths)):
            cmd = (
                "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/plot_ts.py --label=%s  --target=%s --nmonths=%d --rchoice=area"
                % (args.label, args.target, nmonths)
            )
            if mask is not None:
                cmd += " --mask_file=%s" % (mask)
            print(cmd)
            run_cmd(cmd)
        else:
            print("Time-series %s_area_%03d already made" % (mask, nmonths))

# Make adjustments and adjusted dataset for each month
if not os.path.exists("%s/adjusted_target/adjusted_zarr/zarr.json" % (opdir,)):
    cmd = "./make_adjusted_ds_parallel.py "
    cmd += "--label %s " % (args.label)
    cmd += "--target %s " % (args.target)
    cmd += "--convolve=13x13x13 "
    cmd += "--start_year %s --end_year %s " % (str(args.start_year), str(args.end_year))
    # run the output of this command in parallel on spice
    cmd += " | spice_parallel --time=10 --ntasks=2 --mem=16000 --maxjobs=200 "
    print(cmd)
    run_cmd(cmd)
else:
    print("Adjusted target data already made")

# Make stripes plots of the adjusted target
if not os.path.exists("%s/stripes/adjusted_stripes_sample_none.webp" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=16G --cpus-per-task=4 ./stripes/stripes_triple_adjusted.py --label=%s --convolve=none --startyear=%04d --endyear=%04d"
        % (args.label, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Adjusted stripes sample none already made")
if not os.path.exists("%s/stripes/adjusted_stripes_sample_11x13.webp" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=16G --cpus-per-task=4 ./stripes/stripes_triple_adjusted.py --label=%s --convolve=11x13 --startyear=%04d --endyear=%04d  --vmin=0.25 --vmax=0.75"
        % (args.label, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Adjusted stripes sample 11x13 already made")

# Make adjusted time-series
if not os.path.exists("%s/series/None_area_adjusted.pkl" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series_adjusted.py --label=%s  --rchoice=area --startyear=%04d --endyear=%04d"
        % (args.label, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series None_area_adjusted already made")
if not os.path.exists("%s/series/CRU_area_adjusted.pkl" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series_adjusted.py --label=%s  --rchoice=area --mask_file=CRU --startyear=%04d --endyear=%04d"
        % (args.label, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series CRU_area_adjusted already made")
if not os.path.exists("%s/series/Europe_area_adjusted.pkl" % (opdir,)):
    cmd = (
        "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/get_series_adjusted.py --label=%s  --rchoice=area --mask_file=Europe --startyear=%04d --endyear=%04d"
        % (args.label, args.start_year, args.end_year)
    )
    print(cmd)
    run_cmd(cmd)
else:
    print("Time-series Europe_area_adjusted already made")

# Make adjusted time-series plots
for nmonths in [1, 13, 39]:
    for mask in [None, "CRU", "Europe"]:
        if not os.path.exists(
            "%s/series/%s_area_%03d_adjusted.webp" % (opdir, mask, nmonths)
        ):
            cmd = (
                "srun --time=15 --mem=32G --cpus-per-task=4 ./time_series/plot_ts_adjusted.py --label=%s  --target=%s --nmonths=%d --rchoice=area"
                % (args.label, args.target, nmonths)
            )
            if mask is not None:
                cmd += " --mask_file=%s" % (mask)
            print(cmd)
            run_cmd(cmd)
        else:
            print("Adjusted time-series %s_area_%03d already made" % (mask, nmonths))
