A flexible ML model for data transformations
============================================

Following `previous work <http://brohan.org/Proxy_20CR/>`_, we will base our models on the `Deep Convolutional Variational AutoEncoder (VAE) <https://en.wikipedia.org/wiki/Variational_autoencoder>`_. The difference from the previous work is that we are not building a single model - instead we are designing a flexible model that can be used to learn relationships between any of our datasets. The model structure is fixed, but model inputs, outputs and hyperparameters are all taken from a specification file. So we can generate whatever model we need just by changing the specification file.

.. figure:: Model_structure.png
   :width: 95%
   :align: center
   :figwidth: 95%

   The structure of the VAE used to train the generator


The model structure and data flows are defined in files that should not need modification:

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Model structure <VAE>
   Input Datasets <make_dataset>

To run the model, we need to specify the model inputs, outputs and hyperparameters. This is done in a specification file. Copy the specification file and the model training script to a new directory, and edit the specification file to suit your needs. Then run the training script. 

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Specification file <specify>
   Training script <training>

And to test the training success there are scripts for plotting the training history and for testing the model on a test dataset.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Plot training_history <plot_history>
   Validate on single month <validation>
   Validate on time-series <validate_multi>

