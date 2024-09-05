# Specification of the model

# As far as possible, everything specific to the model should be in here

# Then the model spec. and dataset input scripts can be generic.
# Follow the instructions in autoencoder.py to use this.

import tensorflow as tf

specification = {}

specification["modelName"] = "ERA5_P_to_ERA5_P"  # Name of the model

specification["inputTensors"] = ("ERA5_tf_MM/total_precipitation",)
specification["outputTensors"] = (
    "ERA5_tf_MM/total_precipitation",
)  # If None, same as input

specification["outputNames"] = ["Precip"]  # For printout

specification["nInputChannels"] = len(specification["inputTensors"])
if specification["outputTensors"] is not None:
    specification["nOutputChannels"] = len(specification["outputTensors"])
else:
    specification["nOutputChannels"] = specification["nInputChannels"]

specification["startYear"] = None  # Start and end years of training period
specification["endYear"] = None  # (if None, use all available)

specification["testSplit"] = 11  # Keep back test case every n months

# Can use less than all the data (for testing)
specification["maxTrainingMonths"] = None
specification["maxTestMonths"] = None

# Fit parameters
specification["nMonthsInEpoch"] = (
    None  # Length of an epoch - if None, use all the data once
)
specification["nEpochs"] = 5  # How many epochs to train for
specification["shuffleBufferSize"] = 1000  # Buffer size for shuffling
specification["batchSize"] = 32  # Arbitrary
specification["beta"] = 0.00  # Weighting factor for KL divergence of latent space
specification["gamma"] = 0.000  # Weighting factor for KL divergence of output
specification["maxGradient"] = 5  # Numerical instability protection

# Output control
specification["printInterval"] = (
    1  # How often to print metrics and save weights (epochs)
)

# Optimization
specification["strategy"] = tf.distribute.MirroredStrategy()
specification["optimizer"] = tf.keras.optimizers.legacy.Adam(5e-4)
specification["trainCache"] = (
    True  # True might be faster, but needs a *lot* of RAM (try 100Gb) - Also freezes the ensemble members used.
)
specification["testCache"] = (
    True  # True might be faster, but needs a *lot* of RAM (try 100Gb) - Also freezes the ensemble members used.
)


# Mask to specify a subset of data to train on
specification["trainingMask"] = None  # Train on all data
