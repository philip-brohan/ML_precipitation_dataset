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
    fix_lat=None,
    fix_lon=None,
    fix_month=None,
):
    source = None
    target = None
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if start_month is not None and year == start_year and month < start_month:
                continue
            if end_month is not None and year == end_year and month > end_month:
                break
            m_temperature = get_month("temperature", year, month).flatten()
            if no_temperature:
                m_temperature = np.full_like(m_temperature, 0.5)
            m_pressure = get_month("pressure", year, month).flatten()
            if no_pressure:
                m_pressure = np.full_like(m_pressure, 0.5)
            m_precip = get_month("precipitation", year, month).flatten()
            m_latitude = lat_idx.flatten() / 720
            if fix_lat is not None:
                m_latitude = np.full_like(m_latitude, fix_lat / 180 + 0.5)
            m_longitude = lon_idx.flatten() / 1440
            if fix_lon is not None:
                m_longitude = np.full_like(m_longitude, fix_lon / 180 + 0.5)
            m_month = np.full_like(m_temperature, normalize_month(month))
            if fix_month is not None:
                m_month = np.full_like(m_month, normalize_month(fix_month))

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
                m_temperature = m_temperature[sel]
                m_pressure = m_pressure[sel]
                m_precip = m_precip[sel]
                m_latitude = m_latitude[sel]
                m_longitude = m_longitude[sel]
                m_month = m_month[sel]
            # Combine into feature array
            m_source = np.column_stack(
                (m_pressure, m_temperature, m_latitude, m_longitude, m_month)
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
    feature_names = ["pressure", "temperature", "latitude", "longitude", "month"]
    m = xgb.DMatrix(data=source, label=target, feature_names=feature_names)
    return m
