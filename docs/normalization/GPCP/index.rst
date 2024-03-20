Normalizing GPCP
================

.. figure:: ../../../normalize/SPI_monthly/GPCP_tf_MM/monthly.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Raw precipitation (top) and normalized equivalent (bottom) for a month.


.. toctree::
   :titlesonly:
   :maxdepth: 1

    Assemble the raw data <make_raw_tensors>
    Estimating normalization parameters from raw data <estimate_parameters>
    Validating normalization for a selected month <validate_for_month>
    Assemble the normalized data <make_normalized_tensors>

Script to make all the normalization parameters:

.. literalinclude:: ../../../normalize/SPI_monthly/GPCP_tf_MM/make_all_fits.py

