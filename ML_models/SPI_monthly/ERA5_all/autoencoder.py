#!/usr/bin/env python

# Convolutional Variational Autoencoder for ERA5

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

# Load the data path, data source, and model specification
import specify
from makeDataset import getDataset
from autoencoderModel import DCVAE


# Instantiate and run the model under the control of the distribution strategy
with specify.strategy.scope():
    # Set up the training data
    trainingData = getDataset(
        specify.inputTensors, specify.outputTensors, purpose="Train"
    )
    trainingData = trainingData.shuffle(specify.shuffleBufferSize).batch(
        specify.batchSize
    )
    trainingData = specify.strategy.experimental_distribute_dataset(trainingData)

    # Set up the test data
    testData = getDataset(specify.inputTensors, specify.outputTensors, purpose="Test")
    testData = testData.shuffle(specify.shuffleBufferSize).batch(specify.batchSize)
    testData = specify.strategy.experimental_distribute_dataset(testData)

    # Instantiate the model
    autoencoder = DCVAE()

    # If we are doing a restart, load the weights
    if args.epoch > 1:
        weights_dir = ("%s/MLP/%s/weights/Epoch_%04d") % (
            os.getenv("SCRATCH"),
            specify.modelName,
            args.epoch,
        )
        load_status = autoencoder.load_weights("%s/ckpt" % weights_dir)
        load_status.assert_existing_objects_matched()

    # Metrics for training and test loss
    train_rmse = tf.Variable(tf.zeros([specify.nOutputChannels]), trainable=False)
    train_logpz = tf.Variable(0.0, trainable=False)
    train_logqz_x = tf.Variable(0.0, trainable=False)
    train_loss = tf.Variable(0.0, trainable=False)
    test_rmse = tf.Variable(tf.zeros([specify.nOutputChannels]), trainable=False)
    test_logpz = tf.Variable(0.0, trainable=False)
    test_logqz_x = tf.Variable(0.0, trainable=False)
    test_loss = tf.Variable(0.0, trainable=False)
    # And regularization loss
    regularization_loss = tf.Variable(0.0, trainable=False)

    # logfile to output the metrics
    log_FN = ("%s/MLP/%s/logs/Training") % (os.getenv("SCRATCH"), specify.modelName)
    if not os.path.isdir(os.path.dirname(log_FN)):
        os.makedirs(os.path.dirname(log_FN))
    logfile_writer = tf.summary.create_file_writer(log_FN)
    with logfile_writer.as_default():
        tf.summary.write(
            "OutputNames",
            specify.outputNames,
            step=0,
        )

    # For each Epoch: train, save state, and report progress
    for epoch in range(args.epoch, specify.nEpochs + 1):
        start_time = time.time()

        # Train on all batches in the training data
        for batch in trainingData:
            per_replica_op = specify.strategy.run(
                autoencoder.train_on_batch, args=(batch, specify.optimizer)
            )

        end_training_time = time.time()

        # Accumulate average losses over all batches in the validation data
        train_rmse.assign(tf.zeros([specify.nOutputChannels]))
        train_logpz.assign(0.0)
        train_logqz_x.assign(0.0)
        train_loss.assign(0.0)
        validation_batch_count = 0
        for batch in trainingData:
            per_replica_losses = specify.strategy.run(
                autoencoder.compute_loss, args=(batch, False)
            )
            batch_losses = specify.strategy.reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            train_rmse.assign_add(batch_losses[0])
            train_logpz.assign_add(batch_losses[1])
            train_logqz_x.assign_add(batch_losses[2])
            train_loss.assign_add(
                tf.math.reduce_mean(batch_losses[0], axis=0)
                + batch_losses[1]
                + batch_losses[2]
                + batch_losses[3]
            )
            validation_batch_count += 1

        # Same, but for the test data
        test_rmse.assign(tf.zeros([specify.nOutputChannels]))
        test_logpz.assign(0.0)
        test_logqz_x.assign(0.0)
        test_loss.assign(0.0)
        test_batch_count = 0
        for batch in testData:
            per_replica_losses = specify.strategy.run(
                autoencoder.compute_loss, args=(batch, False)
            )
            batch_losses = specify.strategy.reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            test_rmse.assign_add(batch_losses[0])
            test_logpz.assign_add(batch_losses[1])
            test_logqz_x.assign_add(batch_losses[2])
            regularization_loss.assign(batch_losses[3])
            test_loss.assign_add(
                tf.math.reduce_mean(batch_losses[0], axis=0)
                + batch_losses[1]
                + batch_losses[2]
                + batch_losses[3]
            )
            test_batch_count += 1

        # Save model state and current metrics
        save_dir = "%s/MLP/%s/weights/Epoch_%04d" % (
            os.getenv("SCRATCH"),
            specify.modelName,
            epoch,
        )
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        autoencoder.save_weights("%s/ckpt" % save_dir)
        with logfile_writer.as_default():
            tf.summary.write(
                "Train_RMSE",
                train_rmse / validation_batch_count,
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
            tf.summary.write(
                "Test_RMSE",
                test_rmse / (test_batch_count),
                step=epoch,
            )
            tf.summary.scalar("Test_logpz", test_logpz / test_batch_count, step=epoch)
            tf.summary.scalar(
                "Test_logqz_x", test_logqz_x / test_batch_count, step=epoch
            )
            tf.summary.scalar("Test_loss", test_loss / test_batch_count, step=epoch)
            tf.summary.scalar("Regularization_loss", regularization_loss, step=epoch)

        end_monitoring_time = time.time()

        # Report progress
        print("Epoch: {}".format(epoch))
        for i in range(specify.nOutputChannels):
            print(
                "{:<10s}: {:>9.3f}, {:>9.3f}".format(
                    specify.outputNames[i],
                    train_rmse.numpy()[i] / validation_batch_count,
                    test_rmse.numpy()[i] / test_batch_count,
                )
            )
        print(
            "logpz     : {:>9.3f}, {:>9.3f}".format(
                train_logpz.numpy() / validation_batch_count,
                test_logpz.numpy() / test_batch_count,
            )
        )
        print(
            "logqz_x   : {:>9.3f}, {:>9.3f}".format(
                train_logqz_x.numpy() / validation_batch_count,
                test_logqz_x.numpy() / test_batch_count,
            )
        )
        print(
            "regularize:            {:>9.3f}".format(
                regularization_loss.numpy(),
            )
        )
        print(
            "loss      : {:>9.3f}, {:>9.3f}".format(
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
