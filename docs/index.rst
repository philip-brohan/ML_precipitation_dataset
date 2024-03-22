Machine Learning for Precipitation Datasets
===========================================

Precipitation is a difficult variable.

It's not normally distributed, it has low space and time covariance, it's very sensitive to orography (and so to data resolution), and its magnitude varies dramatically between regions and seasons. This means that the various different gridded historical datasets appear very different from one another:

.. figure:: ../visualizations/multi-field/raw_precip/raw_precip.png
   :width: 95%
   :align: center
   :figwidth: 100%

   Precipitation distribution for March 1983 from 5 datasets. (:doc:`Details <visualizations/multi_field_raw_precip>`)

These show precipitation for one month from five different historical datasets (with different data sources, coverage, processing and resolution). They are all plotted on the same scale, and they all use `the same red-blue diverging colourmap <https://matplotlib.org/cmocean/#balance>`_. (If you are wondering where the red is - look closely at the tropical cyclone just off Madagascar). They are clearly similar, but they are not the same, and it's not immediately clear how to quantitatively compare them

With temperature datasets, it's useful to estimate a global mean from each and compare the time-series (`Example <https://climate.metoffice.cloud/temperature.html>`_). This works less well for precipitation:

.. figure:: ../visualizations/raw_time_series/precipitation/precipitation_039.png
   :width: 75%
   :align: center
   :figwidth: 100%

   Global mean monthly mean precipitation time-series from five datasets (with 39-month smoothing). (:doc:`Details <visualizations/multi_field_raw_precip>`)

There are major differences in mean, annual cycle, decadal variability and long-term trends between the datasets. Partly this is a difference in coverage - because precipitation is so much higher in the tropics, the datasets with the best coverage there have the highest global mean. But it's also a difference in the way the data is processed and interpolated. 

To fully understand historical precipitation and its uncertainties, we need to build a consensus between these datasets. We need to understand where the differences are just artefacts of processing, and where they are real differences in the underlying data. We need to understand how to combine these datasets to get the best estimate of the true precipitation, and how to estimate the uncertainty in that estimate. To do this we must model the datasets and their differences, and modern machine learning (ML) offers an ideal toolkit for this: ML is ideally suited to modelling complex, non-linear relationships between variables.

Here we are going to model :doc:`five different gridded datasets of historical monthly average precipitation <get_data/index>`. We will model not only the precipitation, but also other variables (sea-surface temperature, 2m temperature, and sea-level pressure).

In order to model the data, we need to start by normalizing it. ML models work best when the data is normally distributed, and when the variables are on the same scale. We will use a normalization scheme based on the `Standardized Precipitation Index (SPI) <https://climatedataguide.ucar.edu/climate-data/standardized-precipitation-index-spi>`_. SPI is calculated by fitting a `gamma distribution <https://en.wikipedia.org/wiki/Gamma_distribution>`_ to the precipitation data and then, for each point to be normalized, finding the quantile of the data point in that gamma distribution, and replacing the data point with the value which has the same quantile in a standard normal. Effectively this transforms the data, from its original distribution, to a standard normal distribution. (:doc:`Details <normalization/index>`).

.. figure:: ../normalize/SPI_monthly/ERA5_tf_MM/monthly.png
   :width: 95%
   :align: center
   :figwidth: 100%

   Effect of normalization on precipitation data. Top fields are raw precipitation from ERA5, bottom fields are the same data after normalization. (:doc:`Details <normalization/ERA5/validate_for_month>`)

Normalization not only makes the data more suitable for ML, it also makes it easier to compare the datasets. The normalized data is on the same scale, and has the same distribution, so we can directly compare the five different datasets:

.. figure:: ../visualizations/multi-field/normalized_precip/normalized_precip.png
   :width: 95%
   :align: center
   :figwidth: 100%

   Normalized precipitation distribution for March 1983 from 5 datasets. (:doc:`Details <visualizations/multi_field_normalized_precip>`)

And the global mean time-series can now also be meaningfully compared:

.. figure:: ../visualizations/time_series/precipitation/precipitation_039.png
   :width: 95%
   :align: center
   :figwidth: 100%

   Global mean normalized precipitation time-series from five datasets (with 39-month smoothing). (:doc:`Details <visualizations/normalized_precipitation_time_series>`)

We can now see a clear consensus between the datasets over the effect of global warming, as well as large differences in the shorter-term variability. Many of these large differences can be confidently attributed to known inhomogeneities. This can be seen even more clearly by making latitude-time 'stripes' plots, modelled after the `generalized temperature stripes <http://brohan.org/Stripes/>`_.

.. figure:: ../visualizations/stripes/ERA5/total_precipitation_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 100%

   Normalized precipitation stripes from ERA5 (with 11x13 smoothing). (:doc:`Details <visualizations/precipitation_stripes>`)

The stripes for ERA5 show the sudden and dramatic increase in precipitation in about 1980, concentrated in the Southern Hemisphere (where conventional observations are scarce). This is surely an inhomogeneity introduced by the introduction of satellite data. The :doc:`stripes for the other datasets<visualizations/precipitation_stripes>` show similar features, but with different magnitudes and timings.

To quantify the inhomogeneities, we need to model the data. We will follow `previous work <http://brohan.org/Proxy_20CR/>`_ by building a Deep Convolutional Variational Autoencoder (DCVAE) to model the data. This model is a neural network which learns to compress the data into a small number of latent variables, and then reconstruct the data from those variables. The model is trained to minimize the difference between the input and output data, and to maximize the difference between the latent variables and a standard normal distribution. This means that the model learns to compress the data into the most important features, and to ignore the noise. The model can then be used to generate new data, to interpolate between data points, and to identify inhomogeneities. 

A key difference from previous work is that we need to be very flexible in what we model. We will want to model single precipitation datasets (for data assimilation, and inhomogeneity detection), multiple precipitation datasets (to quantify their consistency), and even combinations of precipitation, temperature, and pressure (to use inter-variable consistency as a check on precipitation changes). To handle this we will build a :doc:`generic ML model <ML_generic/index>` which can be easily adapted to different datasets and different variables.

.. figure:: ../ML_models/SPI_monthly/generic_model/comparison.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Validation plot for the generic model applied to three variables from ERA5. 
   Left column\: Target, centre column\: Model output, right column:\ scatter plot. (:doc:`Details <ML_generic/validation>`)

The model is trained on the normalized data, and works well at representing it.

[To be continued].

Appendices
----------

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Selecting, downloading, and handling the data <get_data/index>
   Normalizing the data <normalization/index>
   A flexible Machine Learning model for data transformations <ML_generic/index>
   Visualizations <visualizations/index>
   Utility functions for plotting and re-gridding <utils/index>



Small print
-----------

.. toctree::
   :titlesonly:
   :maxdepth: 1

   How to reproduce or extend this work <how_to>
   Authors and acknowledgements <credits>

  
This document is crown copyright (2024). It is published under the terms of the `Open Government Licence <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/>`_. Source code included is published under the terms of the `BSD licence <https://opensource.org/licenses/BSD-2-Clause>`_.
