Assemble 20CRv3 raw data into a set of tf.tensors
=================================================

The data :doc:`download scripts <../../get_data/TWCR>` assemble selected TWCR data in netCDF files. To use that data efficiently in analysis and modelling it is necessary to reformat it as a set of `tf.tensors`. These have consistent format and resolution and can be reassembled into a `tf.data.Dataset`` for ML model training.

Script to make the set of tensors. Takes argument `--variable`:

.. literalinclude:: ../../../make_raw_tensors/TWCR/make_all_tensors.py

Calls another script to make a single tensor:

.. literalinclude:: ../../../make_raw_tensors/TWCR/make_training_tensor.py

Library functions to convert between `tf.tensor` and `iris.cube.cube`:

.. literalinclude:: ../../../make_raw_tensors/TWCR/tensor_utils.py
   