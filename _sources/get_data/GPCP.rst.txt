GPCP data download and access
=============================

Monthly average precipitation averaged over land and ocean, from a blend of station gauge measurements and satellite observations, are available from `GPCP <https://www.esrl.noaa.gov/psd/data/gridded/data.gpcc.html>`_.

We can download the data from `NOAA <https://downloads.psl.noaa.gov/Datasets/gpcp/precip.mon.mean.nc>`_

Script to do the whole download (about 1.4Gb). Only downloads data where it is not already on disc.

.. literalinclude:: ../../get_data/GPCP/blended/get_means.py

Having downloaded the data, we need to use it. So we need some convenience functions to access the data.

Functions to access downloaded GPCP data:

.. literalinclude:: ../../get_data/GPCP/blended/GPCP_b_monthly.py


