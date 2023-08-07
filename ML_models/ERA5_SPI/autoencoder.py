#!/usr/bin/env python

# Convolutional Variational Autoencoder for ERA5 Precip

import os
import sys
import time
import tensorflow as tf

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--epoch", help="Restart from epoch", type=int, required=False, default=1
)
args = parser.parse_args()

# Distribute across all GPUs
strategy = tf.distribute.MirroredStrategy()
# strategy = tf.distribute.experimental.CentralStorageStrategy()
# strategy = tf.distribute.get_strategy()

# Load the data path, data source, and model specification
from localise import ModelName
from makeDataset import getDataset
from autoencoderModel import DCVAE

# Can use less than all the data (for testing)
nTrainingMonths = None
nTestMonths = None

# How many epochs to train for
nEpochs = 250
# Length of an epoch - if None, same as nTrainingImages
nMonthsInEpoch = None
nRepeatsPerEpoch = 2  # Show each month this many times

if nMonthsInEpoch is None:
    nMonthsInEpoch = nTrainingMonths

# Dataset parameters
bufferSize = 100 #0  # Already shuffled data, so not so important
batchSize = 3 #2  # Arbitrary


# Instantiate and run the model under the control of the distribution strategy
with strategy.scope():
    # Set up the training data
    trainingData = getDataset(
        purpose="training", nMonths=nTrainingMonths, shuffle=True, cache=False
    ).repeat(nRepeatsPerEpoch)
    trainingData = trainingData.shuffle(bufferSize).batch(batchSize)
    trainingData = strategy.experimental_distribute_dataset(trainingData)

    # Subset of the training data for metrics
    validationData = getDataset(
        purpose="training", nMonths=nTestMonths, shuffle=False, cache=False
    )
    validationData = validationData.batch(batchSize)
    validationData = strategy.experimental_distribute_dataset(validationData)

    # Set up the test data
    testData = getDataset(
        purpose="test", nMonths=nTestMonths, shuffle=False, cache=False
    )
    testData = testData.batch(batchSize)
    testData = strategy.experimental_distribute_dataset(testData)

    # Instantiate the model
    autoencoder = DCVAE()
    optimizer = tf.keras.optimizers.Adam(1e-4)
    # If we are doing a restart, load the weights
    if args.epoch > 1:
        weights_dir = ("%s/MLP/%s/weights/Epoch_%04d") % (
            os.getenv("SCRATCH"),
            ModelName,
            args.epoch,
        )
        load_status = autoencoder.load_weights("%s/ckpt" % weights_dir)
        load_status.assert_existing_objects_matched()

    # Metrics for training and test loss
    train_rmse = tf.Variable(0.0, trainable=False)
    train_logpz = tf.Variable(0.0, trainable=False)
    train_logqz_x = tf.Variable(0.0, trainable=False)
    train_loss = tf.Variable(0.0, trainable=False)
    test_rmse = tf.Variable(0.0, trainable=False)
    test_logpz = tf.Variable(0.0, trainable=False)
    test_logqz_x = tf.Variable(0.0, trainable=False)
    test_loss = tf.Variable(0.0, trainable=False)

    # logfile to output the metrics
    log_FN = ("%s/MLP/%s/logs/Training") % (os.getenv("SCRATCH"), ModelName)
    if not os.path.isdir(os.path.dirname(log_FN)):
        os.makedirs(os.path.dirname(log_FN))
    logfile_writer = tf.summary.create_file_writer(log_FN)

    # For each Epoch: train, save state, and report progress
    for epoch in range(args.epoch, nEpochs + 1):
        start_time = time.time()

        # Train on all batches in the training data
        for batch in trainingData:
            per_replica_op = strategy.run(
                autoencoder.train_on_batch, args=(batch, optimizer)
            )

        end_training_time = time.time()

        # Accumulate average losses over all batches in the validation data
        train_rmse.assign(0.0)
        train_logpz.assign(0.0)
        train_logqz_x.assign(0.0)
        train_loss.assign(0.0)
        validation_batch_count = 0
        for batch in validationData:
            per_replica_losses = strategy.run(
                autoencoder.compute_loss, args=(batch, False)
            )
            batch_losses = strategy.reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            train_rmse.assign_add(batch_losses[0])
            train_logpz.assign_add(batch_losses[1])
            train_logqz_x.assign_add(batch_losses[2])
            train_loss.assign_add(tf.math.reduce_sum(batch_losses, axis=0))
            validation_batch_count += 1

        # Same, but for the test data
        test_rmse.assign(0.0)
        test_logpz.assign(0.0)
        test_logqz_x.assign(0.0)
        test_loss.assign(0.0)
        test_batch_count = 0
        for batch in testData:
            per_replica_losses = strategy.run(
                autoencoder.compute_loss, args=(batch, False)
            )
            batch_losses = strategy.reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            test_rmse.assign_add(batch_losses[0])
            test_logpz.assign_add(batch_losses[1])
            test_logqz_x.assign_add(batch_losses[2])
            test_loss.assign_add(tf.math.reduce_sum(batch_losses, axis=0))
            test_batch_count += 1

        # Save model state and current metrics
        save_dir = "%s/MLP/%s/weights/Epoch_%04d" % (
            os.getenv("SCRATCH"),
            ModelName,
            epoch,
        )
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        autoencoder.save_weights("%s/ckpt" % save_dir)
        with logfile_writer.as_default():
            tf.summary.scalar(
                "Train_RMSE",
                100 * train_rmse / (validation_batch_count * autoencoder.RMSE_scale),
                step=epoch,
            )
            tf.summary.scalar(
                "Train_logpz", train_logpz / validation_batch_count, step=epoch
            )
            tf.summary.scalar(
                "Train_logqz_x", train_logqz_x / validation_batch_count, step=epoch
            )
            tf.summary.scalar(
                "Train_loss", train_loss / validation_batch_count, step=epoch
            )
            tf.summary.scalar(
                "Test_RMSE",
                100 * test_rmse / (test_batch_count * autoencoder.RMSE_scale),
                step=epoch,
            )
            tf.summary.scalar("Test_logpz", test_logpz / test_batch_count, step=epoch)
            tf.summary.scalar(
                "Test_logqz_x", test_logqz_x / test_batch_count, step=epoch
            )
            tf.summary.scalar("Test_loss", test_loss / test_batch_count, step=epoch)

        end_monitoring_time = time.time()

        # Report progress
        print("Epoch: {}".format(epoch))
        print(
            "Fit   : {:>9.3f}, {:>9.3f}, {:>6.1f}, {:>6.1f}".format(
                train_rmse.numpy() / validation_batch_count,
                test_rmse.numpy() / test_batch_count,
                100
                * train_rmse.numpy()
                / (validation_batch_count * autoencoder.RMSE_scale),
                100 * test_rmse.numpy() / (test_batch_count * autoencoder.RMSE_scale),
            )
        )
        print(
            "logpz  : {:>9.3f}, {:>9.3f}".format(
                train_logpz.numpy() / validation_batch_count,
                test_logpz.numpy() / test_batch_count,
            )
        )
        print(
            "logqz_x: {:>9.3f}, {:>9.3f}".format(
                train_logqz_x.numpy() / validation_batch_count,
                test_logqz_x.numpy() / test_batch_count,
            )
        )
        print(
            "loss   : {:>9.3f}, {:>9.3f}".format(
                train_loss.numpy() / validation_batch_count,
                test_loss.numpy() / test_batch_count,
            )
        )
        print(
            "time: {} (+{})".format(
                int(end_training_time - start_time),
                int(end_monitoring_time - end_training_time),
            )
        )
