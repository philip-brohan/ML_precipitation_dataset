Normalization
=============

.. figure:: ../../normalize/SPI_monthly/ERA5_tf_MM/monthly.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Raw ERA5 precipitation (top) and normalized equivalent (bottom) for one month.


The normalization scheme used is modelled on the `Standardized Precipitation Index (SPI) <https://climatedataguide.ucar.edu/climate-data/standardized-precipitation-index-spi>`_. SPI is calculated by fitting a gamma distribution to the precipitation data and then, for each point to be normalized, finding the quantile of the data point in that gamma distribution, and replacing the data point with the value which has the same quantile in a standard normal. Effectively this transforms the data, from its original distribution to a standard normal distribution. A different gamma distribution is fitted for each calendar month, and for each grid point.

SPI is designed for fitting precipitation data, but the scheme works for many variables, and we've used it to normalize temperature and pressure data as well.

The gamma distribution fitted is defined by three parameters: the shape, scale and location. The shape and scale are the parameters of the gamma distribution, and the location is the minimum value of the data. The shape and scale are the parameters which are used to calculate the quantile of the data point in the gamma distribution. The location is used to shift the data to the left, so that the gamma distribution can be used to model the data. 

Each dataset used in normalized independently:

.. toctree::
   :titlesonly:
   :maxdepth: 1

    ERA5 <ERA5/index>
    20CR <TWCR/index>
    CRU <CRU/index>
    GPCC <GPCC/index>
    GPCP <GPCP/index>

Script to make all the normalization parameters for all datasets:

.. literalinclude:: ../../normalize/SPI_monthly/normalize_all.sh

Precursor script to assemble the raw data as sets of `tf.tensors`:

.. literalinclude:: ../../make_raw_tensors/make_all_raw_tensors.sh

