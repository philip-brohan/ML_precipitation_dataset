Assemble GPCC normalized data into a set of tf.tensors
======================================================

The data :doc:`download scripts <../../get_data/GPCC>` assemble selected GPCC data in netCDF files. To use that data efficiently in analysis and modelling it is necessary both to normalize it, and to reformat it as a set of `tf.tensors`. These have consistent format and resolution and can be reassembled into a `tf.data.Dataset`` for ML model training.

Script to make the set of tensors. Uses :doc:`precalculated normalization parameters <estimate_parameters>`:

.. literalinclude:: ../../../make_normalized_tensors/GPCC_tf_MM/in_situ/make_all_tensors.py

Calls another script to make a single tensor:

.. literalinclude:: ../../../make_normalized_tensors/GPCC_tf_MM/in_situ/make_training_tensor.py

Library functions to do the normalization:

.. literalinclude:: ../../../normalize/SPI_monthly/GPCC_tf_MM/in_situ/normalize.py

Library functions to convert between `tf.tensor`` and `iris.cube.cube`:

.. literalinclude:: ../../../make_normalized_tensors/GPCC_tf_MM/in_situ/tensor_utils.py
   