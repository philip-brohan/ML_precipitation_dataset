#!/usr/bin/env python

# Find optimum gamma fit parameters using a custom TF model

import os
import sys
import time
import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np

from utilities import grids
from get_data.TWCR import TWCR_monthly_load

rng = np.random.default_rng()

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--month", help="Month to fit", type=int, required=True)
parser.add_argument("--variable", help="Variable", type=str, required=True)
parser.add_argument(
    "--startyear", help="Start Year", type=int, required=False, default=1950
)
parser.add_argument(
    "--endyear", help="End Year", type=int, required=False, default=2014
)
parser.add_argument(
    "--member", help="Ensemble member", type=int, required=False, default=None
)
args = parser.parse_args()

# Distribute across all GPUs
strategy = tf.distribute.MirroredStrategy()

# How many epochs to train for
nEpochs = 250
nRepeatsPerEpoch = 1  # Show each month this many times
bufferSize = 10# 00  # Already shuffled data, so not so important
batchSize = 3# 2  # Arbitrary

# Start training rate
training_rate = 0.1

# Relative scaling factorsm for losses
fit_scale = 1.0
shape_regularization_factor=0.0
scale_regularization_factor=0.0
location_regularization_factor=0.0
shape_neighbour_factor=0.0
scale_neighbour_factor=0.0
location_neighbour_factor=0.0


# Load a pre-prepared tensor from a file
def load_tensor(file_name):
    sict = tf.io.read_file(file_name)
    imt = tf.io.parse_tensor(sict, np.float32)
    imt = tf.reshape(imt, [721, 1440, 1])
    return imt


# Get a list of filenames containing tensors
def getFileNames(variable, month, startyear=1950, endyear=2014):
    inFiles = sorted(
        os.listdir(
            "%s/MLP/normalisation/datasets/raw/%s" % (os.getenv("SCRATCH"), variable)
        )
    )
    inFiles = [
        fn
        for fn in inFiles
        if (
            int(fn[:4]) >= startyear
            and int(fn[5:7]) == month
            and int(fn[:4]) <= endyear
        )
    ]
    return inFiles


# Get a dataset - all the tensors for a given month and variable
def getDataset(variable, month, startyear=1950, endyear=2014, cache=False):
    # Get a list of years to include
    inFiles = getFileNames(variable, month, startyear=startyear, endyear=endyear)

    # Create TensorFlow Dataset object from the source file names
    tn_data = tf.data.Dataset.from_tensor_slices(tf.constant(inFiles))

    # Convert from list of file names to Dataset of source file contents
    fnFiles = [
        "%s/MLP/normalisation/datasets/raw/%s/%s" % (os.getenv("SCRATCH"), variable, x)
        for x in inFiles
    ]
    ts_data = tf.data.Dataset.from_tensor_slices(tf.constant(fnFiles))
    ts_data = ts_data.map(load_tensor, num_parallel_calls=tf.data.experimental.AUTOTUNE)

    # Zip the data together with the years (so we can find the date and source of each
    #   data tensor if we need it).
    tz_data = tf.data.Dataset.zip((ts_data, tn_data))

    # Optimisation
    if cache:
        tz_data = tz_data.cache()  # Great, iff you have enough RAM for it

    tz_data = tz_data.prefetch(tf.data.experimental.AUTOTUNE)

    return tz_data


# Define a TF layer to compare its input against a gamma distribution
# Returns the probability of the inputs given a gamma distribution
#  defined by the layer weights. (Train weights to maximise this).
class GammaC(tf.keras.layers.Layer):
    def __init__(
        self,
    ):
        super().__init__()

    def build(self, input_shape):
        self.shape = self.add_weight(
            shape=input_shape[1:],
            initializer=tf.keras.initializers.Constant(value=1.0),
            trainable=True,
            name='shape',
        )
        self.location = self.add_weight(
            shape=input_shape[1:],
            initializer=tf.keras.initializers.Constant(value=0.0),
            trainable=True,
            name='location',
        )
        self.scale = self.add_weight(
            shape=input_shape[1:],
            initializer=tf.keras.initializers.Constant(value=1.0),
            trainable=True,
            name='scale',
        )

    def call(self, inputs):
        # Constrain scale and shape to be +ve
        dists = tfp.distributions.Gamma(
            concentration=tf.nn.relu(self.scale), rate=1.0 / tf.nn.relu(self.shape)
        )
        # Regularize
        self.add_loss(
            shape_regularization_factor * tf.reduce_mean(tf.square(self.shape))
        )
        self.add_loss(
            scale_regularization_factor * tf.reduce_mean(tf.square(self.scale))
        )
        self.add_loss(
            location_regularization_factor
            * tf.reduce_mean(tf.square(self.location))
        )
        self.add_loss(
            shape_neighbour_factor
            * (
                tf.reduce_mean(tf.square(self.shape[1:, :] - self.shape[:-1, :]))
                + tf.reduce_mean(tf.square(self.shape[:, 1:] - self.shape[:, :-1]))
            )
        )
        self.add_loss(
            scale_neighbour_factor
            * (
                tf.reduce_mean(tf.square(self.scale[1:, :] - self.scale[:-1, :]))
                + tf.reduce_mean(tf.square(self.scale[:, 1:] - self.scale[:, :-1]))
            )
        )
        self.add_loss(
            location_neighbour_factor
            * (
                tf.reduce_mean(tf.square(self.location[1:, :] - self.location[:-1, :]))
                + tf.reduce_mean(
                    tf.square(self.location[:, 1:] - self.location[:, :-1])
                )
            )
        )
        return dists.prob(inputs - self.location)


# Define the model
class Gamma_Fitter(tf.keras.Model):
    # Initialiser - set up instance and define the models
    def __init__(self):
        super(Gamma_Fitter, self).__init__()

        # Hyperparameters
        # Max gradient to apply in optimizer
        self.max_gradient = 2.0

        # Model to encode input to latent space distribution
        self.fitter = tf.keras.Sequential(
            [tf.keras.layers.InputLayer(input_shape=(721, 1440, 1)), GammaC()]
        )

    def call(self, x, training=False):
        probs = self.fitter(x, training=training)
        return probs

    @tf.function
    def compute_loss(self, x, training):
        fit_metric = tf.reduce_mean(tf.square(self.fitter(x[0], training=training)))
        regularization_losses = self.losses
        return tf.stack(
            [
            fit_metric,
            regularization_losses[0],  # shape regularization
            regularization_losses[1],  # scale regularization
            regularization_losses[2],  # location regularization
            regularization_losses[3],  # shape neighbours
            regularization_losses[4],  # scale neighbours
            regularization_losses[5],  # location neighbours
            ]
        )

    # Run the fitter for one batch, calculate the errors, calculate the
    #  gradients and update the layer weights.
    @tf.function
    def train_on_batch(self, x, optimizer):
        with tf.GradientTape() as tape:
            loss_values = self.compute_loss(x, training=True)
            overall_loss = tf.math.reduce_sum(loss_values, axis=0)
        gradients = tape.gradient(overall_loss, self.trainable_variables)
        # Clip the gradients - helps against sudden numerical problems
        gradients = [tf.clip_by_norm(g, self.max_gradient) for g in gradients]
        optimizer.apply_gradients(zip(gradients, self.trainable_variables))


# Instantiate and run the fitter under the control of the distribution strategy
with strategy.scope():
    # Set up the training data
    trainingData = getDataset(
        args.variable,
        args.month,
        startyear=args.startyear,
        endyear=args.endyear,
        cache=False,
    ).repeat(nRepeatsPerEpoch)
    trainingData = trainingData.shuffle(bufferSize).batch(batchSize)
    trainingData = strategy.experimental_distribute_dataset(trainingData)

    # Instantiate the model
    fitter = Gamma_Fitter()
    optimizer = tf.keras.optimizers.Adam(training_rate)

    # Metrics for training loss
    fit_m = tf.Variable(0.0, trainable=False)
    shape_r_m = tf.Variable(0.0, trainable=False)
    scale_r_m = tf.Variable(0.0, trainable=False)
    location_r_m = tf.Variable(0.0, trainable=False)
    shape_n_m = tf.Variable(0.0, trainable=False)
    scale_n_m = tf.Variable(0.0, trainable=False)
    location_n_m = tf.Variable(0.0, trainable=False)
    loss_m = tf.Variable(0.0, trainable=False)

    # logfile to output the metrics
    log_FN = ("%s/MLP/normalisation/logs/%s/Fitting") % (
        os.getenv("SCRATCH"),
        args.variable,
    )
    if not os.path.isdir(os.path.dirname(log_FN)):
        os.makedirs(os.path.dirname(log_FN))
    logfile_writer = tf.summary.create_file_writer(log_FN)

    # For each Epoch: train, save state, and report progress
    for epoch in range(1,nEpochs + 1):
        start_time = time.time()

        # Train on all batches in the training data
        for batch in trainingData:
            per_replica_op = strategy.run(
                fitter.train_on_batch, args=(batch, optimizer)
            )

        end_training_time = time.time()

        # Accumulate average losses over all batches
        fit_m.assign(0.0)
        shape_r_m.assign(0.0)
        scale_r_m.assign(0.0)
        location_r_m.assign(0.0)
        shape_n_m.assign(0.0)
        scale_n_m.assign(0.0)
        location_n_m.assign(0.0)
        loss_m.assign(0.0)
        batch_count = 0
        for batch in trainingData:
            per_replica_losses = strategy.run(fitter.compute_loss, args=(batch, False))
            batch_losses = strategy.reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            fit_m.assign_add(batch_losses[0])
            shape_r_m.assign_add(batch_losses[1])
            scale_r_m.assign_add(batch_losses[2])
            location_r_m.assign_add(batch_losses[3])
            shape_n_m.assign_add(batch_losses[4])
            scale_n_m.assign_add(batch_losses[5])
            location_n_m.assign_add(batch_losses[6])
            loss_m.assign_add(tf.math.reduce_sum(batch_losses, axis=0))
            batch_count += 1

        # Save model state and current metrics
        save_dir = "%s/MLP/fitter/%s/weights/Epoch_%04d" % (
            os.getenv("SCRATCH"),
            args.variable,
            epoch,
        )
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        fitter.save_weights("%s/ckpt" % save_dir)
        with logfile_writer.as_default():
            tf.summary.scalar(
                "Fit",
                fit_m / batch_count,
                step=epoch,
            )
            tf.summary.scalar(
                "Shape regularisation",
                shape_r_m / batch_count,
                step=epoch,
            )
            tf.summary.scalar(
                "Scale regularisation",
                scale_r_m / batch_count,
                step=epoch,
            )
            tf.summary.scalar(
                "Location regularisation",
                location_r_m / batch_count,
                step=epoch,
            )
            tf.summary.scalar(
                "Shape smoothing",
                shape_n_m / batch_count,
                step=epoch,
            )
            tf.summary.scalar(
                "Scale smoothing",
                scale_n_m / batch_count,
                step=epoch,
            )
            tf.summary.scalar(
                "Location smoothing",
                location_n_m / batch_count,
                step=epoch,
            )
            tf.summary.scalar(
                "Loss",
                loss_m / batch_count,
                step=epoch,
            )
        # Report progress
        print("Epoch: {}".format(epoch))
        print(
            "Fit      : {:f}".format(
                fit_m.numpy() / batch_count,
            )
        )
        print(
            "Scale    : {:>9.3f} {:>9.3f}".format(
                scale_r_m.numpy() / batch_count,
                scale_n_m.numpy() / batch_count,
            )
        )
        print(
            "Shape    : {:>9.3f} {:>9.3f}".format(
                shape_r_m.numpy() / batch_count,
                shape_n_m.numpy() / batch_count,
            )
        )
        print(
            "Location : {:>9.3f} {:>9.3f}".format(
                location_r_m.numpy() / batch_count,
                location_n_m.numpy() / batch_count,
            )
        )