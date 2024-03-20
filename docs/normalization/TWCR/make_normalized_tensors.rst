Assemble 20CRv3 normalized data into a set of tf.tensors
========================================================

The data :doc:`download scripts <../../get_data/TWCR>` assemble selected 20CRv3 data in netCDF files. To use that data efficiently in analysis and modelling it is necessary both to normalize it, and to reformat it as a set of `tf.tensors`. These have consistent format and resolution and can be reassembled into a `tf.data.Dataset`` for ML model training.

Script to make the set of tensors. Takes argument `--variable`, and uses :doc:`precalculated normalization parameters <estimate_parameters>`:

.. literalinclude:: ../../../make_normalized_tensors/TWCR_tf_MM/make_all_tensors.py

Calls another script to make a single tensor:

.. literalinclude:: ../../../make_normalized_tensors/TWCR_tf_MM/make_training_tensor.py

Library functions to do the normalization:

.. literalinclude:: ../../../normalize/SPI_monthly/TWCR_tf_MM/normalize.py

Library functions to convert between `tf.tensor`` and `iris.cube.cube`:

.. literalinclude:: ../../../make_normalized_tensors/TWCR_tf_MM/tensor_utils.py
   