#!/usr/bin/env python

# Utility functions for the XGBoost model

import os
import sys
import xgboost as xgb
import numpy as np

rng = np.random.default_rng()


# lat and long indices are the same for all fields
lat_idx = np.transpose(np.tile(np.arange(721, dtype=int), (1440, 1)))
lon_idx = np.tile(np.arange(1440, dtype=int), (721, 1))


# Months are (1..12) want them normalised (0-1) and also switched to sinusoidal
#  seasonal cycle
def normalize_month(month):
    return np.sin(np.pi * (month - 0.5) / 12)


# Get offset monthly data - same as regular data but shifted in lat or lon
def get_month_offset(field, lat_offset=0, lon_offset=0):
    if lat_offset != 0:
        data = np.roll(field, shift=lat_offset, axis=0)
    if lon_offset != 0:
        data = np.roll(field, shift=lon_offset, axis=1)
    return data


# Source is a n*5 array containing 5 features:
#  pressure, temperature, latitude, longitude, month (all normalised)
# Target is an n*1 array containing one feature:
#  precipitation (normalised)
# we add sample rows to each array from each month
def get_source_and_target(
    get_month,
    start_year,
    end_year,
    start_month=None,
    end_month=None,
    samples=None,
    no_temperature=False,
    no_pressure=False,
    no_uwind=False,
    no_vwind=False,
    no_humidity=False,
    fix_lat=None,
    fix_lon=None,
    fix_month=None,
    lat_offset=5,
    lon_offset=5,
):
    source = None
    target = None
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if start_month is not None and year == start_year and month < start_month:
                continue
            if end_month is not None and year == end_year and month > end_month:
                break
            m_precip = get_month("precipitation", year, month).flatten()
            if no_temperature:
                m_temperature = np.full_like(m_precip, 0.5)
                m_temperature_o_lat = m_temperature
                m_temperature_o_lon = m_temperature
            else:
                m_temperature = get_month("temperature", year, month)
                m_temperature_o_lat = get_month_offset(
                    m_temperature, lat_offset=lat_offset, lon_offset=0
                ).flatten()
                m_temperature_o_lon = get_month_offset(
                    m_temperature, lat_offset=0, lon_offset=lon_offset
                ).flatten()
                m_temperature = m_temperature.flatten()
            if no_pressure:
                m_pressure = np.full_like(m_precip, 0.5)
                m_pressure_o_lat = m_pressure
                m_pressure_o_lon = m_pressure
            else:
                m_pressure = get_month("pressure", year, month)
                m_pressure_o_lat = get_month_offset(
                    m_pressure, lat_offset=lat_offset, lon_offset=0
                ).flatten()
                m_pressure_o_lon = get_month_offset(
                    m_pressure, lat_offset=0, lon_offset=lon_offset
                ).flatten()
                m_pressure = m_pressure.flatten()
            if no_uwind:
                m_uwind = np.full_like(m_precip, 0.5)
                m_uwind_o_lat = m_uwind
                m_uwind_o_lon = m_uwind
            else:
                m_uwind = get_month("uwind", year, month)
                m_uwind_o_lat = get_month_offset(
                    m_uwind, lat_offset=lat_offset, lon_offset=0
                ).flatten()
                m_uwind_o_lon = get_month_offset(
                    m_uwind, lat_offset=0, lon_offset=lon_offset
                ).flatten()
                m_uwind = m_uwind.flatten()
            if no_vwind:
                m_vwind = np.full_like(m_precip, 0.5)
                m_vwind_o_lat = m_vwind
                m_vwind_o_lon = m_vwind
            else:
                m_vwind = get_month("vwind", year, month)
                m_vwind_o_lat = get_month_offset(
                    m_vwind, lat_offset=lat_offset, lon_offset=0
                ).flatten()
                m_vwind_o_lon = get_month_offset(
                    m_vwind, lat_offset=0, lon_offset=lon_offset
                ).flatten()
                m_vwind = m_vwind.flatten()
            if no_humidity:
                m_humidity = np.full_like(m_precip, 0.5)
                m_humidity_o_lat = m_humidity
                m_humidity_o_lon = m_humidity
            else:
                m_humidity = get_month("humidity", year, month)
                m_humidity_o_lat = get_month_offset(
                    m_humidity, lat_offset=lat_offset, lon_offset=0
                ).flatten()
                m_humidity_o_lon = get_month_offset(
                    m_humidity, lat_offset=0, lon_offset=lon_offset
                ).flatten()
                m_humidity = m_humidity.flatten()
            if fix_lat is not None:
                m_latitude = np.full_like(m_precip, fix_lat / 180 + 0.5)
            else:
                m_latitude = lat_idx.flatten() / 720
            if fix_lon is not None:
                m_longitude = np.full_like(m_precip, fix_lon / 180 + 0.5)
            else:
                m_longitude = lon_idx.flatten() / 1440
            if fix_month is not None:
                m_month = np.full_like(m_precip, normalize_month(fix_month))
            else:
                m_month = np.full_like(m_temperature, normalize_month(month))

            # Subsample?
            if samples is not None:
                # pick `samples` indices (without replacement) from this month's grid
                npoints = m_temperature.size
                if samples >= npoints:
                    # nothing to do, requested more/equal points than available
                    sel = np.arange(npoints, dtype=int)
                else:
                    sel = rng.choice(npoints, size=samples, replace=False)
                # apply the same selection to all arrays so they stay aligned
                m_precip = m_precip[sel]
                m_temperature = m_temperature[sel]
                m_temperature_o_lat = m_temperature_o_lat[sel]
                m_temperature_o_lon = m_temperature_o_lon[sel]
                m_pressure = m_pressure[sel]
                m_pressure_o_lat = m_pressure_o_lat[sel]
                m_pressure_o_lon = m_pressure_o_lon[sel]
                m_uwind = m_uwind[sel]
                m_uwind_o_lat = m_uwind_o_lat[sel]
                m_uwind_o_lon = m_uwind_o_lon[sel]
                m_vwind = m_vwind[sel]
                m_vwind_o_lat = m_vwind_o_lat[sel]
                m_vwind_o_lon = m_vwind_o_lon[sel]
                m_humidity = m_humidity[sel]
                m_humidity_o_lat = m_humidity_o_lat[sel]
                m_humidity_o_lon = m_humidity_o_lon[sel]
                m_latitude = m_latitude[sel]
                m_longitude = m_longitude[sel]
                m_month = m_month[sel]
            # Combine into feature array
            m_source = np.column_stack(
                (
                    m_pressure,
                    m_pressure_o_lat,
                    m_pressure_o_lon,
                    m_temperature,
                    m_temperature_o_lat,
                    m_temperature_o_lon,
                    m_uwind,
                    m_uwind_o_lat,
                    m_uwind_o_lon,
                    m_vwind,
                    m_vwind_o_lat,
                    m_vwind_o_lon,
                    m_humidity,
                    m_humidity_o_lat,
                    m_humidity_o_lon,
                    m_latitude,
                    m_longitude,
                    m_month,
                )
            )
            # Get this month's target similarly
            m_target = m_precip
            # Concatenate the monthly source and target onto the accumulator arrays
            if source is None:
                source = m_source
                target = m_target
            else:
                source = np.concatenate((source, m_source), axis=0)
                target = np.concatenate((target, m_target), axis=0)
    return source, target


def to_DMatrix(source, target):
    feature_names = [
        "pressure",
        "pressure_o_lat",
        "pressure_o_lon",
        "temperature",
        "temperature_o_lat",
        "temperature_o_lon",
        "uwind",
        "uwind_o_lat",
        "uwind_o_lon",
        "vwind",
        "vwind_o_lat",
        "vwind_o_lon",
        "humidity",
        "humidity_o_lat",
        "humidity_o_lon",
        "latitude",
        "longitude",
        "month",
    ]
    m = xgb.DMatrix(data=source, label=target, feature_names=feature_names)
    return m
