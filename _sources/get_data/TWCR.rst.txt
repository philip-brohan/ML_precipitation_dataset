20CR data download and access
=============================

We are going to use monthly averaged surface variables from `20CRv3 <https://www.esrl.noaa.gov/psd/data/20thC_Rean/>`_.

Four variables:
 * TMP2m
 * SST
 * PRMSL
 * PRATE

We can download all this from the `Ensemble gateway at NERSC <https://portal.nersc.gov/project/20C_Reanalysis/>`_. Note that 20CRv3 is an ensemble product - for each month there are 80 ensemble members. We want them all - we can use them to estimate the uncertainty in the reanalysis.

Script to do the whole download (about 180Gb, will take many hours). Only downloads data where it is not already on disc.

.. literalinclude:: ../../get_data/TWCR/get_data_for_period.py

Script to download a year of TWCR data:

.. literalinclude:: ../../get_data/TWCR/get_year_of_monthlies.py

Having downloaded the data, we need to use it. So we need some convenience functions to access the data.

Functions to access downloaded 20CR data:

.. literalinclude:: ../../get_data/TWCR/TWCR_monthly_load.py



