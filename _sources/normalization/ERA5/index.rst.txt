Normalizing ERA5
================

.. figure:: ../../../normalize/SPI_monthly/ERA5_tf_MM/monthly.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Raw precipitation (top) and normalized precipitation (bottom) for a month.


.. toctree::
   :titlesonly:
   :maxdepth: 1

    Assemble the raw data <make_raw_tensors>
    Validating gamma fits for selected points <validate_for_points>
    Estimating normalization parameters from raw data <estimate_parameters>
    Validating normalization for a selected month <validate_for_month>
    Assemble the normalized data <make_normalized_tensors>

Script to make all the normalization parameters:

.. literalinclude:: ../../../normalize/SPI_monthly/ERA5_tf_MM/make_all_fits.py

