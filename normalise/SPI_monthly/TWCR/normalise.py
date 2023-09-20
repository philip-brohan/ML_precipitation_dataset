# Functions to normalise a data distribution based on SPI
# The aim is to make a normalised distribution that is normally distributed
#  with mean=0.5 and sd=0.2 (so almost all the data is in 0-1)
from scipy.stats import gamma, norm
import numpy as np

import os
import iris
from get_data.TWCR import TWCR_monthly_load


# Load the pre-calculated fitted values
def load_fitted(month, variable="PRATE"):
    shape = iris.load_cube(
        "%s/MLP/normalisation/SPI_monthly/TWCR/%s/shape.nc"
        % (os.getenv("SCRATCH"), variable),
        iris.Constraint(time=lambda cell: cell.point.month == month),
    )
    location = iris.load_cube(
        "%s/MLP/normalisation/SPI_monthly/TWCR/%s/location.nc"
        % (os.getenv("SCRATCH"), variable),
        iris.Constraint(time=lambda cell: cell.point.month == month),
    )
    scale = iris.load_cube(
        "%s/MLP/normalisation/SPI_monthly/TWCR/%s/scale.nc"
        % (os.getenv("SCRATCH"), variable),
        iris.Constraint(time=lambda cell: cell.point.month == month),
    )
    return (shape, location, scale)


# Fit a gamma distribution to the given data
def fit_gamma(raw, variable="PRATE"):
    if variable == "PRATE":
        fit_alpha, fit_loc, fit_beta = gamma.fit(raw, method="MLE", floc=-0.0001)
    else:
        fit_alpha, fit_loc, fit_beta = gamma.fit(raw, method="MLE")
    return (fit_alpha, fit_loc, fit_beta)


# Find the normal variate that matches the gamma cdf
def match_normal(raw, gamma_p, norm_mean=0.5, norm_sd=0.2):
    cdf = gamma.cdf(raw, gamma_p[0], gamma_p[1], gamma_p[2])
    cdf[cdf > 0.99999] = 0.99999  # cdf=0 or 1 causes numerical failure
    cdf[cdf < 0.00001] = 0.00001  # Should fix the gamma fit so this never happens
    spi = norm.ppf(cdf, loc=norm_mean, scale=norm_sd)
    return spi


# Find the original value from the normalised one
def match_original(normalised, gamma_p, norm_mean=0.5, norm_sd=0.2):
    cdf = norm.cdf(normalised, loc=norm_mean, scale=norm_sd)
    original = gamma.ppf(cdf, gamma_p[0], gamma_p[1], gamma_p[2])
    return original


# Normalise a cube (same as match_normal but for cubes)
def normalise_cube(raw, shape, location, scale, norm_mean=0.5, norm_sd=0.2):
    cdf = gamma.cdf(raw.data, shape.data, loc=location.data, scale=scale.data)
    cdf[cdf > 0.99999] = 0.99999  # cdf=0 or 1 causes numerical failure
    cdf[cdf < 0.00001] = 0.00001  # Should fix the gamma fit so this never happens
    spi = norm.ppf(cdf, loc=norm_mean, scale=norm_sd)
    result = raw.copy()
    result.data = spi
    return result


# Convert a cube from normalised value to raw precip
#  (same as match_original but for cubes)
def unnormalise_cube(normalised, shape, location, scale, norm_mean=0.5, norm_sd=0.2):
    cdf = norm.cdf(normalised.data, loc=norm_mean, scale=norm_sd)
    raw = gamma.ppf(cdf, shape.data, location.data, scale.data)
    result = normalised.copy()
    result.data = raw
    return result
