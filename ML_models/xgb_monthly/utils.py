#!/usr/bin/env python

# Utility functions for the XGBoost model (refactored to reduce repetition)

import os
import sys
import xgboost as xgb
import numpy as np

rng = np.random.default_rng()

# lat and long indices are the same for all fields
lat_idx = np.transpose(np.tile(np.arange(721, dtype=int), (1440, 1)))
lon_idx = np.tile(np.arange(1440, dtype=int), (721, 1))


def normalize_month(month):
    """Months are (1..12) -> normalised sinusoidal value (0-1 range-ish)."""
    return np.sin(np.pi * (month - 0.5) / 12)


def get_month_offset(field, lat_offset=0, lon_offset=0):
    """Return a copy of field rolled by given offsets (0 => unchanged)."""
    data = field
    if lat_offset:
        data = np.roll(data, shift=lat_offset, axis=0)
    if lon_offset:
        data = np.roll(data, shift=lon_offset, axis=1)
    return data


def _prepare_field(
    get_month,
    field_name,
    year,
    month,
    base_template,
    lat_offset=None,
    lon_offset=None,
    fill_val=None,
):
    """
    Helper to fetch/prepare a single field and optional offset variants.
    Returns tuple (base_flat, o_lat_flat or None, o_lon_flat or None).
    If fill_val is not None, uses an array filled with fill_val (same shape as base_template).
    """
    if fill_val is None:
        field = get_month(field_name, year, month)
    else:
        field = np.full_like(base_template, fill_val)

    base_flat = field.flatten()

    o_lat = None
    o_lon = None
    if lat_offset is not None:
        o_lat = get_month_offset(field, lat_offset=lat_offset, lon_offset=0).flatten()
    if lon_offset is not None:
        o_lon = get_month_offset(field, lat_offset=0, lon_offset=lon_offset).flatten()

    return base_flat, o_lat, o_lon


def get_source_and_target(
    get_s_month,
    get_t_month,
    start_year,
    end_year,
    start_month=None,
    end_month=None,
    samples=None,
    no_temperature=False,
    no_pressure=False,
    no_pressure_sd=False,
    no_uwind=False,
    no_vwind=False,
    no_humidity=False,
    fix_lat=None,
    fix_lon=None,
    fix_month=None,
    lat_offset=None,
    lon_offset=None,
):
    """
    Build source (features) and target (precipitation) arrays across months/years.
    Uses helper functions to avoid repetitive code.
    Returns (source, target, feature_names) where feature_names matches source columns.
    """
    source = None
    target = None
    feature_names_out = None

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if start_month is not None and year == start_year and month < start_month:
                continue
            if end_month is not None and year == end_year and month > end_month:
                break

            # precipitation (target)
            m_precip_field = get_t_month("precipitation", year, month)
            m_precip = m_precip_field.flatten()

            # base template for full_like fills
            base_template = m_precip_field

            # Prepare each field (base, offset-lat, offset-lon)
            m_temperature, m_temperature_o_lat, m_temperature_o_lon = _prepare_field(
                get_s_month,
                "temperature",
                year,
                month,
                base_template,
                lat_offset=lat_offset,
                lon_offset=lon_offset,
                fill_val=0.5 if no_temperature else None,
            )
            m_pressure, m_pressure_o_lat, m_pressure_o_lon = _prepare_field(
                get_s_month,
                "pressure",
                year,
                month,
                base_template,
                lat_offset=lat_offset,
                lon_offset=lon_offset,
                fill_val=0.5 if no_pressure else None,
            )
            m_pressure_sd, m_pressure_sd_o_lat, m_pressure_sd_o_lon = _prepare_field(
                get_s_month,
                "pressure_sd",
                year,
                month,
                base_template,
                lat_offset=lat_offset,
                lon_offset=lon_offset,
                fill_val=0.5 if no_pressure_sd else None,
            )
            m_uwind, m_uwind_o_lat, m_uwind_o_lon = _prepare_field(
                get_s_month,
                "uwind",
                year,
                month,
                base_template,
                lat_offset=lat_offset,
                lon_offset=lon_offset,
                fill_val=0.5 if no_uwind else None,
            )
            m_vwind, m_vwind_o_lat, m_vwind_o_lon = _prepare_field(
                get_s_month,
                "vwind",
                year,
                month,
                base_template,
                lat_offset=lat_offset,
                lon_offset=lon_offset,
                fill_val=0.5 if no_vwind else None,
            )
            m_humidity, m_humidity_o_lat, m_humidity_o_lon = _prepare_field(
                get_s_month,
                "humidity",
                year,
                month,
                base_template,
                lat_offset=lat_offset,
                lon_offset=lon_offset,
                fill_val=0.5 if no_humidity else None,
            )

            # latitude / longitude / month
            if fix_lat is not None:
                m_latitude = np.full_like(m_precip, fix_lat / 180 + 0.5)
            else:
                m_latitude = lat_idx.flatten() / 720

            if fix_lon is not None:
                m_longitude = np.full_like(m_precip, fix_lon / 180 + 0.5)
            else:
                m_longitude = lon_idx.flatten() / 1440

            if fix_month is not None:
                m_month = np.full_like(m_temperature, normalize_month(fix_month))
            else:
                m_month = np.full_like(m_temperature, normalize_month(month))

            # Subsample selection (apply same sel to all arrays)
            sel = None
            if samples is not None:
                npoints = m_temperature.size
                if samples >= npoints:
                    sel = np.arange(npoints, dtype=int)
                else:
                    sel = rng.choice(npoints, size=samples, replace=False)

            def _apply_sel(arr):
                return arr if sel is None else arr[sel]

            # Apply selection to all arrays (including offset variants if present)
            m_precip_s = _apply_sel(m_precip)
            m_temperature_s = _apply_sel(m_temperature)
            m_pressure_s = _apply_sel(m_pressure)
            m_uwind_s = _apply_sel(m_uwind)
            m_vwind_s = _apply_sel(m_vwind)
            m_humidity_s = _apply_sel(m_humidity)
            m_latitude_s = _apply_sel(m_latitude)
            m_longitude_s = _apply_sel(m_longitude)
            m_month_s = _apply_sel(m_month)

            # Offsets
            def _maybe_sel(arr):
                return None if arr is None else _apply_sel(arr)

            m_temperature_o_lat_s = _maybe_sel(m_temperature_o_lat)
            m_temperature_o_lon_s = _maybe_sel(m_temperature_o_lon)
            m_pressure_o_lat_s = _maybe_sel(m_pressure_o_lat)
            m_pressure_o_lon_s = _maybe_sel(m_pressure_o_lon)
            m_uwind_o_lat_s = _maybe_sel(m_uwind_o_lat)
            m_uwind_o_lon_s = _maybe_sel(m_uwind_o_lon)
            m_vwind_o_lat_s = _maybe_sel(m_vwind_o_lat)
            m_vwind_o_lon_s = _maybe_sel(m_vwind_o_lon)
            m_humidity_o_lat_s = _maybe_sel(m_humidity_o_lat)
            m_humidity_o_lon_s = _maybe_sel(m_humidity_o_lon)

            # Build named columns in the same order as feature_names in to_DMatrix()
            cols_named = [
                ("pressure", m_pressure_s),
                ("pressure_o_lat", m_pressure_o_lat_s),
                ("pressure_o_lon", m_pressure_o_lon_s),
                ("temperature", m_temperature_s),
                ("temperature_o_lat", m_temperature_o_lat_s),
                ("temperature_o_lon", m_temperature_o_lon_s),
                ("uwind", m_uwind_s),
                ("uwind_o_lat", m_uwind_o_lat_s),
                ("uwind_o_lon", m_uwind_o_lon_s),
                ("vwind", m_vwind_s),
                ("vwind_o_lat", m_vwind_o_lat_s),
                ("vwind_o_lon", m_vwind_o_lon_s),
                ("humidity", m_humidity_s),
                ("humidity_o_lat", m_humidity_o_lat_s),
                ("humidity_o_lon", m_humidity_o_lon_s),
                ("latitude", m_latitude_s),
                ("longitude", m_longitude_s),
                ("month", m_month_s),
            ]

            # Filter out None columns and keep matching names
            cols_filtered = [arr for (name, arr) in cols_named if arr is not None]
            names_filtered = [name for (name, arr) in cols_named if arr is not None]

            m_source = np.column_stack(tuple(cols_filtered))
            m_target = m_precip_s

            # Set feature names on first encounter (they're constant across months)
            if feature_names_out is None:
                feature_names_out = names_filtered

            # Concatenate month onto accumulator arrays
            if source is None:
                source = m_source
                target = m_target
            else:
                source = np.concatenate((source, m_source), axis=0)
                target = np.concatenate((target, m_target), axis=0)

    return source, target, feature_names_out


def to_DMatrix(source, target, feature_names=None):
    """
    Build xgboost DMatrix. If feature_names is provided use it, otherwise
    fall back to the legacy full-name list (keeps backward compatibility).
    """
    if feature_names is None:
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
