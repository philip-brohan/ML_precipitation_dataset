CRU data download and access
============================

Monthly average precipitation averaged over land, from station gauge measurements, are available from `CRU <https://crudata.uea.ac.uk/cru/data/hrg/>`_.

We can download the data from the awesome `Copernicus Climate Data Store <https://cds.climate.copernicus.eu/cdsapp#!/home>`_

Script to do the whole download (about 6Gb). Only downloads data where it is not already on disc.

.. literalinclude:: ../../get_data/CRU/in_situ/get_data_for_period.py

Script to download a year of CRU data:

.. literalinclude:: ../../get_data/CRU/in_situ/get_year_of_monthlies.py

Having downloaded the data, we need to use it. So we need some convenience functions to access the data.

Functions to access downloaded CRU data:

.. literalinclude:: ../../get_data/CRU/in_situ/CRU_i_monthly.py


