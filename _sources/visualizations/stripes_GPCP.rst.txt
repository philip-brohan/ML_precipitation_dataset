Visualizations - GPCP stripes
=============================

.. figure:: ../../visualizations/stripes/GPCP/Precip_sample_none.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized :doc:`precipitation stripes <precipitation_stripes>` from GPCP.

.. figure:: ../../visualizations/stripes/GPCP/Precip_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but with an 11x13 filter.


Script (`make_all.sh`) to regenerate all the GPCP stripes plots.

.. literalinclude:: ../../visualizations/stripes/GPCP/make_all.sh
    :language: bash

Script (`stripes.py`) to make the plot for an individual variable. Takes arguments `--variable` to pick the variable, `--convolve` to apply a filter, and `--startyear`, `--endyear`, `--vmin`, and `--vmax` to set the range of years and the colour scale.

.. literalinclude:: ../../visualizations/stripes/GPCP/stripes.py
    :language: python

The data are taken from the `tf.tensor` datasets of normalized data created during the normalization process. `makeDataset.py` is a library to present these as a `tf.data.Dataset`.

.. literalinclude:: ../../visualizations/stripes/GPCP/makeDataset.py
    :language: python
