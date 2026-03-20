A Homogenized Precipitation Dataset
===================================

Precipitation is a difficult variable.

It's not normally distributed, it has low space and time covariance, it's very sensitive to orography (and so to data resolution), and its magnitude varies dramatically between regions and seasons. So let's start from something easier - near-surface temperature anomaly, simply expressed:

.. figure:: https://brohan.org/Stripes/_images/HadCRUT5.png
   :width: 95%
   :align: center
   :figwidth: 100%

   Traditional `climate stripes <https://en.wikipedia.org/wiki/Warming_stripes/>`_ - global-mean, annual-mean temperature anomalies (w.r.t. 1961-90) from the HadCRUT5 dataset. (`Figure source <https://brohan.org/Stripes/>`_).

This is clear and powerful, but not very informative. It doesn't show the spatial or seasonal structure of the data, and it doesn't show any of the uncertainty or give insight into possible biases. To look at the data in more detail we can use the `Extended Stripes <https://brohan.org/Stripes>`_:

.. figure:: https://brohan.org/Stripes/_images/HadCRUT5_sample_3x3.png
   :width: 95%
   :align: center
   :figwidth: 100%

   Monthly temperature anomalies (w.r.t. 1961-90) from the HadCRUT5 dataset after regridding to a 0.25 degree latitude resolution. The vertical axis is latitude (South Pole at the bottom, North Pole at the top), and each pixel is from a randomly selected longitude and ensemble member. Grey areas show regions where HadCRUT5 has no data. (`Figure source <https://brohan.org/Stripes/comparisons2.html>`_).

This version has sacrificed the beautiful simplicity of the original stripes, but it is *enormously* more informative. It shows the spatial and seasonal structure of the data, and it shows the places where observations are unavailable (the grey areas). This is starting to be useful for dataset construction and evaluation, but it's still a bit noisy - in the extratropics there is a lot of high-frequency weather-driven variability, which makes it hard to see the underlying climate signal and any possible biases present. To get around this, one approach is to quantile-normalise the data before making the plot:

.. figure:: images/HadCRUT_normalized_stripes_T_sample_11x13.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Same as the plot above, except that the data have been standardized to be normally distributed on the range 0-1 (approximately) at each grid-point, for each calendar month.  (:doc:`Normalization process <normalization/index>`, `Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/visualizations/stripes/HadCRUT>`_). This image has a slightly different colour map and spatial smoothing to the one above, so it looks a little different, but the underlying data are the same.
   
Standardized data has three advantages - interesting structure in the data stands out more clearly (for example the super-El-Nino of 1878, and the widespread cold period shortly after 1900), standardization is a requirement for modelling the data with Machine Learning tools, and we can make similar standardized plots from different base datasets, which makes it easier to compare them. And this brings us back to precipitation:

.. figure:: images/TWCR_normalized_stripes_PRATE_sample_11x13.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Same as the plot above, but for precipitation rate from the Twentieth Century Reanalysis (20CRv3) dataset. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/visualizations/stripes/TWCR>`_).
 
The challenges of working with precipitation are immediately apparent. In the temperature plot, the data are dominated by strong signals (global warming, ENSO, the Early-20th-Century warming) with some contamination from biases and noise (the widespread cold at the beginning of the 20th Century, for example, is likely bias). In the precipitation plot, some signal is visible (the late-20th Century moistening, some ENSO features, ...) but most of the visible signal is bias - the strong drying in the south is almost certainly a reflection of a sea-ice bias in the HadISST dataset, which is used as a boundary condition in 20CRv3, and the tropical shifts in the 19th Century are probably a result of model bias in the reanalysis showing up in places where there are too few pressure observations to constrain the reanalysis properly. (I'm not sure whether the shifts in the far north are real or not).

To look at biases in more detail, we can look, not just at 20CRv3, but at a range of decent datasets. We will compare five different datasets - two reanalyses, two gridded observational datasets, and a blended satellite-based dataset. 

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Selecting, downloading, and handling the data <get_data/index>
   Normalizing each dataset <normalization/index>

We can then see the problem of pervasive bias by comparing global mean precipitation time-series from all the datasets:

.. figure:: images/time_series_nomodel_None_area_precipitation_039.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Global mean standardized precipitation rate from a range of datasets, including reanalyses, gridded observations, and a satellite-based dataset. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/visualizations/time_series/precipitation>`_).


.. figure:: images/time_series_nomodel_Europe_area_precipitation_039.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Same as the figure above, but a mean over the European region (35-65N, 15W-30E) instead of the global mean.

Modelling precipitation with a decision tree
--------------------------------------------


.. figure:: images/XGBoost.png
   :width: 95%
   :align: center
   :figwidth: 100%

   A decision tree model can be trained to estimate precipitation from relatively reliable surface fields.


.. figure:: images/time_series_TWCR_to_TWCR_None_area_013.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Global mean standardized precipitation rate from 20CRv3, and as calculated from a decision tree model (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/ML_models/xgb_monthly/time_series>`_).


.. toctree::
   :titlesonly:
   :maxdepth: 1

   Details of the model specification and fitting process <fit_model>
   Validation of the model fit with 20CRv3 data <xgb_model_fits/TWCR_to_TWCR>


.. toctree::
   :titlesonly:
   :maxdepth: 1

   Inhomogeneities in the 20CRv3 surface fields <20CRv3_homogeneity>
   Inhomogeneities in the ERA5 surface fields <ERA5_homogeneity>


.. figure:: images/time_series_TWCR_to_ERA5_None_area_013.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Same as the plot above, but using a model trained to predict ERA5 precipitation using 20CRv3 temperature, pressure, wind and humidity (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/tree/f30502ac9296f4b88c18562c1e635a4572b0c375/ML_models/xgb_monthly/time_series>`_).


.. toctree::
   :titlesonly:
   :maxdepth: 1

   Validation of the model fit to ERA5 precipitation using 20CRv3 surface variables <xgb_model_fits/TWCR_to_ERA5>

Building a homogenized version of ERA5 precipitation
----------------------------------------------------

.. figure:: images/time_series_TWCR_to_ERA5_None_area_013_adjusted.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Global mean standardized precipitation rate from ERA5, and the same after adjustment to remove inhomogeneities using 20CRv3 surface variables (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/ML_models/xgb_monthly/time_series/plot_ts_adjusted.py>`_).


Conclusions
-----------

* Precipitation is a difficult variable, and all datasets - even the best - have substantial biases and inhomogeneities.
* These biases and inhomogeneities can be identified and visualized using the extended-stripes approach, especially if the data are standardized first.
* Decision Tree models can be trained to predict precipitation from more reliable surface variables. This can be used to identify inhomogeneities in the data.
* Unfortunately, even relatively reliable surface variables (temperature, pressure, ...) have significant inhomogeneities in the reanalysis datasets, especially early in the record, they can't be treated as a reliable source before about 1950.
* Subtracting the modelled precipitation from the original data can be used to estimate inhomogeneities, and subtracting these estimated inhomogeneities from the original data produces a homogenized version of the ERA5 precipitation record. This is far from perfect, but it does remove some of the most egregious inhomogeneities, and it is a step towards a more reliable precipitation dataset.
* A desirable next step would be to use a similar approach to homogenize other variables (temperature, pressure, sea-ice, ...) and so to make a more homogenous long-term reanalysis.


Small print
-----------

.. toctree::
   :titlesonly:
   :maxdepth: 1

   How to reproduce or extend this work <how_to>
   Authors and acknowledgements <credits>

  
This document is crown copyright (2026). It is published under the terms of the `Open Government Licence <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/>`_. Source code included is published under the terms of the `BSD licence <https://opensource.org/licenses/BSD-2-Clause>`_.
