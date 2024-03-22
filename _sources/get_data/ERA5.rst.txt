ERA5 data download and access
=============================

We are going to use monthly averaged surface variables from `ERA5 <https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5>`_.

Four variables:
 * 2m_temperature
 * sea_surface_temperature
 * mean_sea_level_pressure
 * total_precipitation

We can download all this from the awesome `Copernicus Climate Data Store <https://cds.climate.copernicus.eu/cdsapp#!/home>`_

Script to do the whole download (about 8Gb, will take a few hours). Only downloads data where it is not already on disc.

.. literalinclude:: ../../get_data/ERA5/get_data_for_period_ERA5.py

Script to download a year of ERA5 data:   

.. literalinclude:: ../../get_data/ERA5/get_year_of_monthlies_from_ERA5.py

Having downloaded the data, we need to use it. So we need some convenience functions to access the data.

Functions to access downloaded ERA5 data:

.. literalinclude:: ../../get_data/ERA5/ERA5_monthly.py



