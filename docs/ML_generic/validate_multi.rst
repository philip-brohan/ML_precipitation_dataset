Generic model - validate trained model on time-series of all test months
========================================================================

.. figure:: ../../ML_models/SPI_monthly/generic_model/multi.webp
   :width: 95%
   :align: center
   :figwidth: 95%

   Global mean series (black original, red DCVAE output) and scatterplots for each output variable.

Script (`validate_multi.py`) to make the validation figure

By default, it will use the test set, but the `--training` argument will take months from the training set instead of the test set.

.. literalinclude:: ../../ML_models/SPI_monthly/generic_model/validate_multi.py

Utility functions used in the plot

.. literalinclude:: ../../ML_models/SPI_monthly/generic_model/gmUtils.py




