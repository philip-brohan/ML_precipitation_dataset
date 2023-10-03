#!/usr/bin/env python

# Find optimum gamma fit parameters using a custom TF model

import os
import sys
import time
import tensorflow as tf

from makeDataset import getDataset
from fitterModel import Gamma_Fitter

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
bufferSize = 10  # 00  # Already shuffled data, so not so important
batchSize = 3  # 2  # Arbitrary

# Start training rate
training_rate = 1

# Instantiate and run the fitter under the control of the distribution strategy
with strategy.scope():
    # Set up the training data
    trainingData = getDataset(
        args.variable,
        args.month,
        startyear=args.startyear,
        endyear=args.endyear,
        cache=True,
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
    for epoch in range(1, nEpochs + 1):
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
        print(
            "time: {} ".format(
                int(end_training_time - start_time),
            )
        )
