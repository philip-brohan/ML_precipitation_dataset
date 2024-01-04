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
from specify import specification
from makeDataset import getDataset
from autoencoderModel import DCVAE


# Get Datasets
def getDatasets():
    # Set up the training data
    trainingData = getDataset(specification, purpose="Train")
    trainingData = trainingData.shuffle(specification["shuffleBufferSize"]).batch(
        specification["batchSize"]
    )
    trainingData = specification["strategy"].experimental_distribute_dataset(
        trainingData
    )

    # Set up the test data
    testData = getDataset(specification, purpose="Test")
    testData = testData.shuffle(specification["shuffleBufferSize"]).batch(
        specification["batchSize"]
    )
    testData = specification["strategy"].experimental_distribute_dataset(testData)

    return (trainingData, testData)


# Load model and initial weights
def getModel(epoch=1):
    # Instantiate the model
    autoencoder = DCVAE(specification)

    # If we are doing a restart, load the weights
    if epoch > 1:
        weights_dir = ("%s/MLP/%s/weights/Epoch_%04d") % (
            os.getenv("SCRATCH"),
            specification["modelName"],
            args.epoch,
        )
        load_status = autoencoder.load_weights("%s/ckpt" % weights_dir)
        load_status.assert_existing_objects_matched()

    return autoencoder


# Instantiate and run the model under the control of the distribution strategy
with specification["strategy"].scope():
    trainingData, testData = getDatasets()

    autoencoder = getModel(epoch=args.epoch)

    # logfile to output the metrics
    log_FN = ("%s/MLP/%s/logs/Training") % (
        os.getenv("SCRATCH"),
        specification["modelName"],
    )
    if not os.path.isdir(os.path.dirname(log_FN)):
        os.makedirs(os.path.dirname(log_FN))
    logfile_writer = tf.summary.create_file_writer(log_FN)
    with logfile_writer.as_default():
        tf.summary.write(
            "OutputNames",
            specification["outputNames"],
            step=0,
        )

    # For each Epoch: train, save state, and report progress
    for epoch in range(args.epoch, specification["nEpochs"] + 1):
        start_time = time.time()

        # Train on all batches in the training data
        for batch in trainingData:
            per_replica_op = specification["strategy"].run(
                autoencoder.train_on_batch, args=(batch, specification["optimizer"])
            )

        end_training_time = time.time()

        # Accumulate average losses over all batches in the validation data
        autoencoder.update_metrics(trainingData, testData)

        # Save model state
        save_dir = "%s/MLP/%s/weights/Epoch_%04d" % (
            os.getenv("SCRATCH"),
            specification["modelName"],
            epoch,
        )
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        autoencoder.save_weights("%s/ckpt" % save_dir)

        # Update the log file with current metrics
        autoencoder.updateLogfile(logfile_writer, epoch)

        end_monitoring_time = time.time()

        # Report progress
        print("Epoch: {}".format(epoch))
        autoencoder.printState()
        print(
            "time: {} (+{})".format(
                int(end_training_time - start_time),
                int(end_monitoring_time - end_training_time),
            )
        )
