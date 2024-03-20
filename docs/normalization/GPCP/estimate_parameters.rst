Estimate normalization parameters for GPCP data
===============================================

.. figure:: ../../../normalize/SPI_monthly/GPCP_tf_MM/gamma.png
   :width: 65%
   :align: center
   :figwidth: 95%

   Fitted gamma distribution parameters for GPCP precipitation. Top\: location, centre\: shape, bottom\: scale.

Script to make normalization parameters for one calendar month. Takes arguments `--month`, `-variable`, `--startyear`, and `--endyear`:

.. literalinclude:: ../../../normalize/SPI_monthly/GPCP_tf_MM/fit_for_month.py

The data are taken from the `tf.tensor` datasets of raw data created during the normalization process. Functions to present these as `tf.data.DataSets`:

.. literalinclude:: ../../../normalize/SPI_monthly/GPCP_tf_MM/makeDataset.py

Script to plot the fitted gamma parameters (produces figure at top of page):

.. literalinclude:: ../../../normalize/SPI_monthly/GPCP_tf_MM/plot_gamma_fit.py
   