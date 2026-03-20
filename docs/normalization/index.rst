Normalization
=============

We are not going to analyse or model the raw precipitation data (in m/s). First, we're going to normalize it.

.. figure:: ../images/normalisation_monthly_TWCR_PRATE.webp
   :width: 95%
   :align: center
   :figwidth: 95%

   Raw 20CRv3 precipitation (top) and normalized equivalent (bottom) for one month. The top panel is green where there is lots of precipitation, the bottom panel is green where there is more precipitation than expected for that location and time of year. The data are the same in the two cases, but the normalized data is more informative, spatially homogenous, and normally distributed - better for almost every purpose. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/normalize/SPI_monthly/TWCR_tf_MM/plot_distribution_monthly.py>`_).

Why normalize?
--------------

Raw precipitation varies enormously between times and places. This makes it difficult to analyse and model, and to compare between times and places. 

.. figure:: ../images/multi_field_raw_precip.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Raw precipitation fields for one month from :doc:`five different datasets <../get_data/index>`. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/visualizations/multi-field/raw_precip/plot_fields.py>`_). This image uses a standard red-blue colour scheme, but you'll have to look closely to see the red pixels (there's a tropical storm off Madagascar). The massive heterogeneity in the data makes it difficult to see much.

Massive spatial heterogeneity also means that a global average is not very meaningful.

.. figure:: ../images/raw_time_series_precipitation_039.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Global mean precipitation from the five datasets - smoothed with a 39-month running mean to make it easier to see the trends. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/visualizations/raw_time_series/precipitation/plot_series.py>`_).

So before we do anything else, we normalize the data.

The normalization scheme used is modelled on the `Standardized Precipitation Index (SPI) <https://climatedataguide.ucar.edu/climate-data/standardized-precipitation-index-spi>`_. SPI is calculated by fitting a gamma distribution to the precipitation data and then, for each point to be normalized, finding the quantile of the data point in that gamma distribution, and replacing the data point with the value which has the same quantile in a standard normal. Effectively this transforms the data, from its original distribution to a standard normal distribution. A different gamma distribution is fitted for each calendar month, and for each grid point.

SPI is designed for fitting precipitation data, but the scheme works for many variables, and we've used it to normalize temperature, pressure, wind and humidity as well.

The gamma distribution fitted is defined by three parameters: the shape, scale and location. The shape and scale are the parameters of the gamma distribution, and the location is the minimum value of the data. The shape and scale are the parameters which are used to calculate the quantile of the data point in the gamma distribution. The location is used to shift the data to the left, so that the gamma distribution can be used to model the data. 

So the Process of normalization is as follows:

* Assemble the raw data as `zarr files <https://zarr.dev/>`_ setup for efficient access as `TensorFlow tf.tensors <https://www.tensorflow.org/api_docs/python/tf/Tensor>`_ 
* From the raw data, estimate the gamma distribution parameters for each calendar month and grid point.
* Use the fitted gamma distribution parameters to transform the raw data to normalized data, and assemble this as ``zarr files`` of ``tf.tensors`` for efficient access in analysis and modelling.

Each dataset used is normalized independently:

* 20CRv3: `Assemble raw data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_raw_tensors/ERA5>`_, `estimate normalisation parameters <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/normalize/SPI_monthly/ERA5_tf_MM>`_, `assemble normalized data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_normalized_tensors/ERA5_tf_MM>`_.
* ERA5: `Assemble raw data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_raw_tensors/TWCR>`_, `estimate normalisation parameters <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/normalize/SPI_monthly/TWCR_tf_MM>`_, `assemble normalized data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_normalized_tensors/TWCR_tf_MM>`_.
* CRU: `Assemble raw data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_raw_tensors/CRU>`_, `estimate normalisation parameters <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/normalize/SPI_monthly/CRU_tf_MM>`_, `assemble normalized data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_normalized_tensors/CRU_tf_MM>`_.
* GPCC: `Assemble raw data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_raw_tensors/GPCC>`_, `estimate normalisation parameters <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/normalize/SPI_monthly/GPCC_tf_MM>`_, `assemble normalized data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_normalized_tensors/GPCC_tf_MM>`_.
* GPCP: `Assemble raw data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_raw_tensors/GPCP>`_, `estimate normalisation parameters <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/normalize/SPI_monthly/GPCP_tf_MM>`_, `assemble normalized data <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_normalized_tensors/GPCP_tf_MM>`_.

.

* `Script to assemble the raw data for all datasets <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_raw_tensors/make_all_raw_tensors.sh>`_.


* `Script to make all the normalization parameters for all datasets <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/normalize/SPI_monthly/normalize_all.sh>`_.


* `Script to assemble the normalized data for all datasets <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/make_normalized_tensors/make_all_normalized_tensors.sh>`_.

Normalized data
---------------

.. figure:: ../images/multi_field_normalized_precip.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same figure as above, but showing the normalized precipitation fields. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/visualizations/multi-field/normalized_precip/plot_fields.py>`_). 

.. figure:: ../images/time_series_nomodel_None_area_precipitation_039.webp
   :width: 95%
   :align: center
   :figwidth: 95%

   Same figure as above, but showing the global-average normalized precipitation time-series. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/visualizations/time_series/precipitation>`_). 
