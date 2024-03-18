Visualizations - raw precipitation time-series
==============================================

.. figure:: ../../visualizations/raw_time_series/precipitation/precipitation_001.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Global mean raw precipitation time-series. No smoothing.


.. figure:: ../../visualizations/raw_time_series/precipitation/precipitation_039.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but smoothed with a 39-month running mean.


Script (`get_series.py`) collects the global means.

.. literalinclude:: ../../visualizations/raw_time_series/precipitation/get_series.py
    :language: python

Script (`plot_series.py`) makes the plot. Takes optional arguments `--nmonths` to specify the number of months to smooth over, `--start_year` and `--end_year` to specify the time period to plot, `--ymin` and `--ymax` to specify the y-axis limits, and `--linewidth` for cosmetic effect.

.. literalinclude:: ../../visualizations/raw_time_series/precipitation/plot_series.py
    :language: python

The data are taken from the `tf.tensor` datasets of raw data created during the normalization process. There is a separate script for each dataset to present these as `tf.data.DataSets`:

.. literalinclude:: ../../visualizations/raw_time_series/precipitation/ERA5Dataset.py
    :language: python