# Specification of the model

# As far as possible, everything specific to the model should be in here

# Then the model spec. and dataset input scripts can be generic.
# Follow the instructions in autoencoder.py to use this.

import tensorflow as tf

specification = {}
specification["strategy"] = tf.distribute.MirroredStrategy()
# specification["strategy"] = tf.distribute.experimental.CentralStorageStrategy()
# specification["strategy"] = tf.distribute.get_strategy()
with specification["strategy"].scope():

    specification["modelName"] = "Hourly"

    specification["inputTensors"] = ("TWCR_tf_MM/TMP2m", "TWCR_tf_MM/PRMSL")
    specification["outputTensors"] = (
        "TWCR_tf_MM/TMP2m",
        "TWCR_tf_MM/PRMSL",
        "TWCR_tf_MM/PRATE",
    )  # If None, same as input

    specification["outputNames"] = ["T2m", "PRMSL", "Precip"]  # For printout

    specification["nInputChannels"] = len(specification["inputTensors"])
    if specification["outputTensors"] is not None:
        specification["nOutputChannels"] = len(specification["outputTensors"])
    else:
        specification["nOutputChannels"] = specification["nInputChannels"]

    specification["startYear"] = None  # Start and end years of training period
    specification["endYear"] = None  # (if None, use all available)

    specification["testSplit"] = 11  # Keep back test case every n months

    # Can use less than all the data (for testing)
    specification["maxTrainingHours"] = 10000
    specification["maxTestHours"] = 100

    # Fit parameters
    specification["nHoursInEpoch"] = (
        None  # Length of an epoch - if None, use all the data once
    )
    specification["nEpochs"] = 1000  # How many epochs to train for
    specification["shuffleBufferSize"] = 1000  # Buffer size for shuffling
    specification["batchSize"] = 32  # Arbitrary
    specification["beta"] = 0.00  # Weighting factor for KL divergence of latent space
    specification["gamma"] = 0.000  # Weighting factor for KL divergence of output
    specification["maxGradient"] = 2  # Numerical instability protection

    # Output control
    specification["printInterval"] = (
        1  # How often to print metrics and save weights (epochs)
    )

    # Optimization
    specification["optimizer"] = tf.keras.optimizers.Adam(1e-3)
    specification["trainCache"] = (
        True  # True might be faster, but needs a *lot* of RAM - Also freezes the ensemble members used.
    )
    specification["testCache"] = (
        True  # True might be faster, but needs a *lot* of RAM - Also freezes the ensemble members used.
    )

    # Mask to specify a subset of data to train on
    specification["trainingMask"] = None  # Train on all data
