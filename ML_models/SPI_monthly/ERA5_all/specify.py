# Specification of the model

# As far as possible, everything specific to the model should be in here

# Then the model spec, training control, and dataset input scripts
#  can be generic.

import tensorflow as tf

modelName = "ERA5_all"

inputTensors = (
    "ERA5_tf_MM/2m_temperature",
    "ERA5_tf_MM/sea_surface_temperature",
    "ERA5_tf_MM/mean_sea_level_pressure",
    "ERA5_tf_MM/total_precipitation",
)
outputTensors = None  # If None, same as input

outputNames = (
    "T2m",
    "SST",
    "MSLP",
    "Precip",
)  # For printout

nInputChannels = len(inputTensors)
if outputTensors is not None:
    nOutputChannels = len(outputTensors)
else:
    nOutputChannels = nInputChannels

startYear = None  # Start and end years of training period
endYear = None  # (if None, use all available)

testSplit = 11  # Keep back test case evey n months

# Can use less than all the data (for testing)
maxTrainingMonths = None
maxTestMonths = None

# What to do if there is more than one field/month
maxEnsembleCombinations = 5  # Every possible combination of ensembles can get large
correlatedEnsembles = (
    False  # Ensemble member 1 in source 1 matches member 1 in source 2
)

# Fit parameters
nMonthsInEpoch = None  # Length of an epoch - if None, use all the data once
nEpochs = 250  # How many epochs to train for
shuffleBufferSize = 100  # Already shuffled data, so not so important
batchSize = 32  # Arbitrary
beta = 0.001  # Weighting factor for KL divergence error term
regularizationScale = 0.01  # Weighting factor for regularization loss
latentDimension = 100  # Embedding dimension
maxGradient = 5  # Numerical instability protection

# Optimization
strategy = tf.distribute.MirroredStrategy()
optimizer = tf.keras.optimizers.Adam(1e-3)
trainCache = False
testCache = False
