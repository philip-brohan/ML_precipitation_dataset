# Functions to normalise a data distribution based on SPI
# The aim is to make a normalised distribution that is normally distributed
#  with mean=0.5 and sd=0.2 (so almost all the data is in 0-1)
from scipy.stats import gamma, norm


# Fit a gamma distribution to the given data
def fit_gamma(raw):
    fit_alpha, fit_loc, fit_beta = gamma.fit(raw)
    return (fit_alpha, fit_loc, fit_beta)


# Find the normal variate that matches the gamma cdf
def match_normal(raw, gamma_p, norm_mean=0.5, norm_sd=0.2):
    cdf = gamma.cdf(raw, gamma_p[0], gamma_p[1], gamma_p[2])
    spi = norm.pdf(cdf, loc=norm_mean, scale=norm_sd)
    return spi


# Find the original value from the normalised one
def match_original(normalised, gamma_p, norm_mean=0.5, norm_sd=0.2):
    cdf = norm.cdf(normalised, loc=norm_mean, scale=norm_sd)
    original = gamma.pdf(cdf, gamma_p[0], gamma_p[1], gamma_p[2])
    return original
