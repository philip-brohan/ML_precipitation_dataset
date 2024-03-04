A flexible ML model for data transformations
============================================

Following `previous work <http://brohan.org/Proxy_20CR/>`_,
 we will base our models on the `Deep Convolutional Variational AutoEncoder (VAE) <https://en.wikipedia.org/wiki/Variational_autoencoder>`_. The difference from the previous work is that we are not building a single model - instead we are designing a flexible model that can be used to learn relationships between any of our datasets. The model structure is fixed, but model inputs, outputs and hyperparameters are all taken from a specification file. So we can generate whatever model we need just by changing the specification file.

.. figure:: Model_structure.png
   :width: 95%
   :align: center
   :figwidth: 95%

   The structure of the VAE used to train the generator



.. toctree::
   :titlesonly:
   :maxdepth: 1

   Specification file <specification>
   Make the training datasets <make_dataset>
   Fundamental model structure <VAE>
   Train the model <training>
   Validate the trained model <validation>

