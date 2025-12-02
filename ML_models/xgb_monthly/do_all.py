#!/usr/bin/env python

# Prepare data, train a model, and make validation plots.

import os

import argparse

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
    cmd += "--label train "
    cmd += "--source %s " % (args.source)
    cmd += "--target %s " % (args.target)
    print(cmd)
    os.system(cmd)
else:
    print("Training data already made")

# Make the test data if it does not already exist
if not os.path.exists("%s/%s_test.dt" % (opdir, args.source)):
    # Prepare the training data
    cmd = "srun --time=60 --mem=32G ./make_dmatrix.py --opdir=%s " % (opdir,)
    if args.no_pressure:
        cmd += "--no_pressure "
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
    os.system(cmd)
else:
    print("Test data already made")

# Train the model if not already done
if not os.path.exists("%s/%s.ubj" % (opdir, args.source)):
    cmd = "srun --time=30 --mem=32G --cpus-per-task=4 ./fit_model.py "
    cmd += "--mlabel=%s/%s " % (
        args.label,
        args.source,
    )
    cmd += "--label %s/%s_train " % (args.label, args.source)
    cmd += "--test_label %s/%s_test " % (args.label, args.source)
    cmd += "> %s/train.log " % (opdir,)
    print(cmd)
    os.system(cmd)
else:
    print("Model already trained")

# Make test:train validation plot
if not os.path.exists("%s/test_train.webp" % (opdir,)):
    cmd = "srun --time=5 --mem=16G --cpus-per-task=4 ./validate_2.py "
    cmd += "--mlabel1 %s/%s " % (args.label, args.source)
    cmd += "--label1 %s/%s_train " % (args.label, args.source)
    cmd += "--mlabel2 %s/%s " % (args.label, args.source)
    cmd += "--label2 %s/%s_test " % (args.label, args.source)
    cmd += "--out %s/test_train.webp " % (opdir,)
    print(cmd)
    os.system(cmd)
else:
    print("Test:train validation plot already made")

# Make monthly validation plot
if not os.path.exists("%s/monthly.webp" % (opdir,)):
    cmd = "srun --time=5 --mem=32G --cpus-per-task=2 ./validate_month.py "
    cmd += "--mlabel %s/%s " % (args.label, args.source)
    cmd += "--source %s " % (args.source,)
    cmd += "--target %s " % (args.target)
    cmd += "--out %s/monthly.webp " % (opdir,)
    if args.no_pressure:
        cmd += "--no_pressure "
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
    os.system(cmd)
else:
    print("Monthly validation plot already made")

# Make time series validation plot
if not os.path.exists("%s/time_series_validation.webp" % (opdir,)):
    cmd = "./validate_time_series_parallel.py "
    cmd += "--mlabel %s/%s " % (args.label, args.source)
    cmd += "--label %s " % (args.label)
    cmd += "--source %s " % (args.source,)
    cmd += "--target %s " % (args.target)
    if args.no_pressure:
        cmd += "--no_pressure "
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
    cmd += " | spice_parallel --time=30 --ntasks=4 --mem=32000 "
    print(cmd)
    os.system(cmd)
    cmd = "./plot_ts_validation.py --label=%s " % (args.label,)
    cmd += "--out %s/time_series_validation.webp " % (opdir,)
    print(cmd)
    os.system(cmd)
else:
    print("Time-series validation plot already made")
