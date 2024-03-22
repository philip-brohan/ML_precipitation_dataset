Assemble GPCP raw data into a set of tf.tensors
===============================================

The data :doc:`download scripts <../../get_data/GPCP>` assemble selected GPCP data in netCDF files. To use that data efficiently in analysis and modelling it is necessary to reformat it as a set of `tf.tensors`. These have consistent format and resolution and can be reassembled into a `tf.data.Dataset`` for ML model training.

Script to make the set of tensors:

.. literalinclude:: ../../../make_raw_tensors/GPCP/blended/make_all_tensors.py

Calls another script to make a single tensor:

.. literalinclude:: ../../../make_raw_tensors/GPCP/blended/make_training_tensor.py

Library functions to convert between `tf.tensor` and `iris.cube.cube`:

.. literalinclude:: ../../../make_raw_tensors/GPCP/blended/tensor_utils.py
   