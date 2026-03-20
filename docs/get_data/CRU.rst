CRU data download and access
============================

Monthly average precipitation averaged over land, from station gauge measurements, are available from `CRU <https://crudata.uea.ac.uk/cru/data/hrg/>`_.

We can download the data from the awesome `Copernicus Climate Data Store <https://cds.climate.copernicus.eu/cdsapp#!/home>`_

* `Script to do the whole download (about 6Gb) <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/get_data/CRU/in_situ/get_data_for_period.py>`_. Only downloads data where it is not already on disc.
* `Script to download a year of CRU data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/get_data/CRU/in_situ/get_year_of_monthlies.py>`_.

Having downloaded the data, we need to use it. So we need some convenience functions to access the data.

* `Functions to access downloaded CRU data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/get_data/CRU/in_situ/CRU_i_monthly.py>`_.


