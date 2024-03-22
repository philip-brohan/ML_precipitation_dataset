Visualizations - ERA5 stripes
=============================

.. figure:: ../../visualizations/stripes/ERA5/2m_temperature_sample_none.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized :doc:`temperature stripes <temperature_stripes>` from ERA5.

.. figure:: ../../visualizations/stripes/ERA5/2m_temperature_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but with an 11x13 filter.

.. figure:: ../../visualizations/stripes/ERA5/mean_sea_level_pressure_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized :doc:`pressure stripes <pressure_stripes>` from ERA5. With an 11x13 filter.

.. figure:: ../../visualizations/stripes/ERA5/total_precipitation_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized :doc:`precipitation stripes <precipitation_stripes>` from ERA5. With an 11x13 filter.


Script (`make_all.sh`) to regenerate all the ERA5 stripes plots.

.. literalinclude:: ../../visualizations/stripes/ERA5/make_all.sh
    :language: bash

Script (`stripes.py`) to make the plot for an individual variable. Takes arguments `--variable` to pick the variable, `--convolve` to apply a filter, and `--startyear`, `--endyear`, `--vmin`, and `--vmax` to set the range of years and the colour scale.

.. literalinclude:: ../../visualizations/stripes/ERA5/stripes.py
    :language: python

The data are taken from the `tf.tensor` datasets of normalized data created during the normalization process. `makeDataset.py` is a library to present these as a `tf.data.Dataset`.

.. literalinclude:: ../../visualizations/stripes/ERA5/makeDataset.py
    :language: python
