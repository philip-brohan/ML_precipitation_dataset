Visualizations - 20CRv3 stripes
===============================

.. figure:: ../../visualizations/stripes/TWCR/TMP2m_sample_none.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized :doc:`temperature stripes <temperature_stripes>` from TWCR.

.. figure:: ../../visualizations/stripes/TWCR/TMP2m_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but with an 11x13 filter.

.. figure:: ../../visualizations/stripes/TWCR/PRMSL_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized :doc:`pressure stripes <pressure_stripes>` from TWCR. With an 11x13 filter.

.. figure:: ../../visualizations/stripes/TWCR/PRATE_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized :doc:`precipitation stripes <precipitation_stripes>` from TWCR. With an 11x13 filter.


Script (`make_all.sh`) to regenerate all the TWCR stripes plots.

.. literalinclude:: ../../visualizations/stripes/TWCR/make_all.sh
    :language: bash

Script (`stripes.py`) to make the plot for an individual variable. Takes arguments `--variable` to pick the variable, `--convolve` to apply a filter, and `--startyear`, `--endyear`, `--vmin`, and `--vmax` to set the range of years and the colour scale.

.. literalinclude:: ../../visualizations/stripes/TWCR/stripes.py
    :language: python

The data are taken from the `tf.tensor` datasets of normalized data created during the normalization process. `makeDataset.py` is a library to present these as a `tf.data.Dataset`.

.. literalinclude:: ../../visualizations/stripes/TWCR/makeDataset.py
    :language: python
