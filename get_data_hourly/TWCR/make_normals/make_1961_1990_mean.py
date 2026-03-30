#!/usr/bin/env python

"""Create a 1961-1990 hourly climatological mean for one calendar day/hour."""

import argparse
import datetime
import iris

from get_data_hourly.TWCR import TWCR_hourly_load


START_YEAR = 1961
END_YEAR = 1990


def _parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Calculate the 1961-1990 mean field for a specific month/day/hour "
            "using TWCR_hourly_load.load_hourly_member."
        )
    )
    parser.add_argument(
        "--variable",
        type=str,
        default="PRATE",
        help="TWCR variable name (e.g. PRATE, TMP2m, PRMSL, SST)",
    )
    parser.add_argument("--month", type=int, required=True, help="Month number 1-12")
    parser.add_argument("--day", type=int, required=True, help="Day number 1-31")
    parser.add_argument(
        "--hour",
        type=int,
        required=True,
        help="Hour UTC (0,3,6,...,21)",
    )
    parser.add_argument(
        "--member",
        type=int,
        default=None,
        help=(
            "Single ensemble member to use. If omitted, uses the subset in "
            "TWCR_hourly_load.members"
        ),
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output NetCDF path for the mean cube",
    )
    return parser.parse_args()


def _validate_inputs(month, day, hour):
    if month < 1 or month > 12:
        raise ValueError("--month must be in 1..12")
    if hour < 0 or hour > 23 or hour % 3 != 0:
        raise ValueError("--hour must be one of 0,3,6,...,21")
    # Validate day against a leap year so Feb 29 can be requested.
    try:
        datetime.datetime(1964, month, day, hour)
    except ValueError as exc:
        raise ValueError(f"Invalid month/day/hour combination: {exc}") from exc


def main():
    args = _parse_args()
    _validate_inputs(args.month, args.day, args.hour)

    if args.member is None:
        members = list(TWCR_hourly_load.members)
    else:
        members = [args.member]

    mean = TWCR_hourly_load.load_hourly_climatology(
        variable=args.variable,
        month=args.month,
        day=args.day,
        hour=args.hour,
        members_to_use=members,
        start_year=START_YEAR,
        end_year=END_YEAR,
    )

    print(
        "Computed mean for "
        f"{args.variable} m={args.month:02d} d={args.day:02d} h={args.hour:02d} "
        f"over 1961-1990 using {mean.attributes['n_samples']} samples"
    )

    if args.output is not None:
        iris.save(mean, args.output)
        print(f"Saved mean cube: {args.output}")


if __name__ == "__main__":
    main()
