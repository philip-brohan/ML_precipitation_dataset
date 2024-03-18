Visualizations - normalized temperature time-series
===================================================

.. figure:: ../../visualizations/time_series/temperature/temperatures_001.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Global mean normalized temperature time-series. No smoothing.


.. figure:: ../../visualizations/time_series/temperature/temperatures_039.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but smoothed with a 39-month running mean.


Script (`get_series.py`) collects the global means.

.. literalinclude:: ../../visualizations/time_series/temperature/get_series.py
    :language: python

Script (`plot_series.py`) makes the plot. Takes optional arguments `--nmonths` to specify the number of months to smooth over, `--start_year` and `--end_year` to specify the time period to plot, `--ymin` and `--ymax` to specify the y-axis limits, and `--linewidth` for cosmetic effect.

.. literalinclude:: ../../visualizations/time_series/temperature/plot_series.py
    :language: python

The data are taken from the `tf.tensor` datasets of normalized data created during the normalization process. The libraries to present these as `tf.data.Dataset` objects are in the :doc:` stripes directory <../stripes_ERA5>`.
