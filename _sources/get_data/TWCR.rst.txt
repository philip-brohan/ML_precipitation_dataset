20CR data download and access
=============================

We are going to use monthly averaged surface variables from `20CRv3 <https://www.esrl.noaa.gov/psd/data/20thC_Rean/>`_.

Four variables:
 * TMP2m
 * SST
 * PRMSL
 * PRATE

We can download all this from the `Ensemble gateway at NERSC <https://portal.nersc.gov/project/20C_Reanalysis/>`_. Note that 20CRv3 is an ensemble product - for each month there are 80 ensemble members. We want them all - we can use them to estimate the uncertainty in the reanalysis.

* `Script to do the whole download (about 180Gb, will take many hours) <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/get_data/TWCR/get_data_for_period.py>`_. Only downloads data where it is not already on disc.

* `Script to download a year of TWCR data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/get_data/TWCR/get_year_of_monthlies.py>`_.

Having downloaded the data, we need to use it. So we need some convenience functions to access the data.

* `Functions to access downloaded 20CR data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/get_data/TWCR/TWCR_monthly_load.py>`_.

We also want one additional variable - the monthly standard deviation of PRMSL. This isn't available as monthly data, so we need to download the hourly PRMSL and calculate the monthly sd.

* `Script to do the whole hourly PRMSL download (about 5Tb, will take *many* hours) <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/get_data_hourly/TWCR/hourly_from_nersc.sh>`_.
* `Script to download a year of hourly PRMSL <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/get_data_hourly/TWCR/v3_release_from_nersc.py>`_.
* `Script to calculate the monthly sd of PRMSL from the hourly data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_monthly_sd/make_sd.py>`_.


