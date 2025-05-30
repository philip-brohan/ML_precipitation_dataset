# Specify a Deep Convolutional Variational AutoEncoder

# This is a generic model that can be used for any set of input and output fields
# Follow the instructions in autoencoder.py to use it for a specific model.

import os
import sys
import tensorflow as tf
from tensorflow.keras.layers import (
    Input,
    Dense,
    Activation,
    BatchNormalization,
    Dropout,
    MaxPooling2D,
    Conv2D,
    concatenate,
    Conv2DTranspose,
)


class UNet(tf.keras.Model):
    # Initialiser - set up instance and define the models
    def __init__(self, specification, **kwargs):
        super(UNet, self).__init__(**kwargs)
        self.specification = specification

        # Model to convert input to output
        BASE_FILTERS = 32
        INPUT_SIZE = (256, 512, self.specification["nInputChannels"])
        DROPOUT = 0.4
        ACTIVATION = "relu"
        INITIALIZER = "he_normal"

        input_layer = Input(INPUT_SIZE)

        c1 = Conv2D(
            BASE_FILTERS,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(input_layer)
        c1 = BatchNormalization()(c1)
        c1 = Dropout(DROPOUT)(c1)
        c1 = Conv2D(
            BASE_FILTERS,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c1)
        c1 = BatchNormalization()(c1)
        p1 = MaxPooling2D((2, 2))(c1)

        c2 = Conv2D(
            BASE_FILTERS * 2,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(p1)
        c2 = BatchNormalization()(c2)
        c2 = Dropout(DROPOUT)(c2)
        c2 = Conv2D(
            BASE_FILTERS * 2,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c2)
        c2 = BatchNormalization()(c2)
        p2 = MaxPooling2D((2, 2))(c2)

        c3 = Conv2D(
            BASE_FILTERS * 4,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(p2)
        c3 = BatchNormalization()(c3)
        c3 = Dropout(DROPOUT)(c3)
        c3 = Conv2D(
            BASE_FILTERS * 4,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c3)
        c3 = BatchNormalization()(c3)
        p3 = MaxPooling2D((2, 2))(c3)

        c4 = Conv2D(
            BASE_FILTERS * 8,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(p3)
        c4 = BatchNormalization()(c4)
        c4 = Dropout(DROPOUT)(c4)
        c4 = Conv2D(
            BASE_FILTERS * 8,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c4)
        c4 = BatchNormalization()(c4)
        p4 = MaxPooling2D(pool_size=(2, 2))(c4)

        c5 = Conv2D(
            BASE_FILTERS * 16,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(p4)
        c5 = BatchNormalization()(c5)
        c5 = Dropout(DROPOUT)(c5)
        c5 = Conv2D(
            BASE_FILTERS * 16,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c5)
        c5 = BatchNormalization()(c5)

        u6 = Conv2DTranspose(BASE_FILTERS * 8, (2, 2), strides=(2, 2), padding="same")(
            c5
        )
        u6 = concatenate([u6, c4])
        c6 = Conv2D(
            BASE_FILTERS * 8,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(u6)
        c6 = BatchNormalization()(c6)
        c6 = Dropout(DROPOUT)(c6)
        c6 = Conv2D(
            BASE_FILTERS * 8,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c6)
        c6 = BatchNormalization()(c6)

        u7 = Conv2DTranspose(BASE_FILTERS * 4, (2, 2), strides=(2, 2), padding="same")(
            c6
        )
        u7 = concatenate([u7, c3])
        c7 = Conv2D(
            BASE_FILTERS * 4,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(u7)
        c7 = BatchNormalization()(c7)
        c7 = Dropout(DROPOUT)(c7)
        c7 = Conv2D(
            BASE_FILTERS * 4,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c7)
        c7 = BatchNormalization()(c7)

        u8 = Conv2DTranspose(BASE_FILTERS * 2, (2, 2), strides=(2, 2), padding="same")(
            c7
        )
        u8 = concatenate([u8, c2])
        c8 = Conv2D(
            BASE_FILTERS * 2,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(u8)
        c8 = BatchNormalization()(c8)
        c8 = Dropout(DROPOUT)(c8)
        c8 = Conv2D(
            BASE_FILTERS * 2,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c8)
        c8 = BatchNormalization()(c8)

        u9 = Conv2DTranspose(BASE_FILTERS, (2, 2), strides=(2, 2), padding="same")(c8)
        u9 = concatenate([u9, c1], axis=3)
        c9 = Conv2D(
            BASE_FILTERS,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(u9)
        c9 = BatchNormalization()(c9)
        c9 = Dropout(DROPOUT)(c9)
        c9 = Conv2D(
            BASE_FILTERS,
            (3, 3),
            activation=ACTIVATION,
            kernel_initializer=INITIALIZER,
            padding="same",
        )(c9)

        ouput_layer = Conv2D(
            self.specification["nOutputChannels"], (1, 1), activation=None
        )(c9)

        # Make that chain of layers into a callabble model
        self.transform = tf.keras.Model(inputs=input_layer, outputs=ouput_layer)

        # Metrics for training and test loss
        self.train_rmse = tf.Variable(
            tf.zeros([self.specification["nOutputChannels"]]), trainable=False
        )
        self.train_rmse_m = tf.Variable(
            tf.zeros([self.specification["nOutputChannels"]]), trainable=False
        )
        self.train_logpz = tf.Variable(0.0, trainable=False)
        self.train_logqz_x = tf.Variable(0.0, trainable=False)
        self.train_logpz_g = tf.Variable(0.0, trainable=False)
        self.train_logqz_g = tf.Variable(0.0, trainable=False)
        self.train_loss = tf.Variable(0.0, trainable=False)
        self.test_rmse = tf.Variable(
            tf.zeros([self.specification["nOutputChannels"]]), trainable=False
        )
        self.test_rmse_m = tf.Variable(
            tf.zeros([self.specification["nOutputChannels"]]), trainable=False
        )
        self.test_logpz = tf.Variable(0.0, trainable=False)
        self.test_logqz_x = tf.Variable(0.0, trainable=False)
        self.test_logpz_g = tf.Variable(0.0, trainable=False)
        self.test_logqz_g = tf.Variable(0.0, trainable=False)
        self.test_loss = tf.Variable(0.0, trainable=False)
        # And regularization loss
        self.regularization_loss = tf.Variable(0.0, trainable=False)

    # Convert a batch of inputs to one of outputs
    def call(self, x, training=True):
        generated = self.transform(x[1], training=training)
        return generated

    # Utility function to calculate fit of sample to N(mean,logvar)
    # Used in loss calculation
    def log_normal_pdf(self, sample, mean, logvar, raxis=1):
        log2pi = tf.math.log(2.0 * 3.141592653589793)
        return tf.reduce_sum(
            -0.5 * ((sample - mean) ** 2.0 * tf.exp(-logvar) + logvar + log2pi),
            axis=raxis,
        )

    @tf.function
    def fit_loss(self, generated, target, climatology):
        # Metric is fractional variance reduction compared to climatology
        weights = tf.where(target != 0.0, 1.0, 0.0)  # Missing data zero weighted
        # Keep the last dimension (different variables)
        skill = tf.reduce_sum(
            tf.math.squared_difference(generated, target) * weights, axis=[0, 1, 2]
        ) / tf.reduce_sum(weights, axis=[0, 1, 2])
        guess = tf.reduce_sum(
            tf.math.squared_difference(climatology, target) * weights, axis=[0, 1, 2]
        ) / tf.reduce_sum(weights, axis=[0, 1, 2])
        return skill / guess

    # Calculate the losses from autoencoding a batch of inputs
    # We are calculating a seperate loss for each variable, and for for the
    #  two components of the latent space KLD regularizer. This is useful
    #  for monitoring and debugging, but the weight update only depends
    #  on a single value (their sum).
    @tf.function
    def compute_loss(self, x, training):
        generated = self.transform(x[1], training=training)

        gV = generated
        cV = gV * 0.0 + 0.5  # Climatology
        tV = x[-1]
        fit_metric = self.fit_loss(gV, tV, cV)

        regularization = 0.0  # tf.add_n(self.losses)

        return (
            fit_metric,
            regularization,
        )

    # Run the autoencoder for one batch, calculate the errors, calculate the
    #  gradients and update the layer weights.
    @tf.function
    def train_on_batch(self, x, ignore):
        with tf.GradientTape() as tape:
            loss_values = self.compute_loss(x, training=True)
            overall_loss = (
                tf.math.reduce_mean(loss_values[0], axis=0)  # RMSE
                + loss_values[1]  # Regularization
            )
        gradients = tape.gradient(overall_loss, self.trainable_variables)
        # Clip the gradients - helps against sudden numerical problems
        if self.specification["maxGradient"] is not None:
            gradients = [
                tf.clip_by_norm(g, self.specification["maxGradient"]) for g in gradients
            ]
        self.specification["optimizer"].apply_gradients(
            zip(gradients, self.trainable_variables)
        )

    # Update the metrics
    def update_metrics(self, trainDS, testDS):
        self.train_rmse.assign(tf.zeros([self.specification["nOutputChannels"]]))
        self.train_rmse_m.assign(tf.zeros([self.specification["nOutputChannels"]]))
        self.train_loss.assign(0.0)
        validation_batch_count = 0
        for batch in trainDS:
            # Metrics over masked area
            if (
                self.specification["trainingMask"] is not None
            ):  # Metrics over masked area
                mbatch = tf.where(
                    self.specification["trainingMask"] == 0, batch[-1], 0.0
                )
                per_replica_losses = self.specification["strategy"].run(
                    self.compute_loss, args=((batch[:-1], mbatch), False)
                )
                batch_losses = self.specification["strategy"].reduce(
                    tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
                )
                self.train_rmse_m.assign_add(batch_losses[0])
            # Metrics over unmasked area
            if self.specification["trainingMask"] is not None:
                mbatch = tf.where(
                    self.specification["trainingMask"] != 0, batch[-1], 0.0
                )
                batch = (batch[:-1], mbatch)
            per_replica_losses = self.specification["strategy"].run(
                self.compute_loss, args=(batch, False)
            )
            batch_losses = self.specification["strategy"].reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            self.train_rmse.assign_add(batch_losses[0])
            self.train_loss.assign_add(
                tf.math.reduce_mean(batch_losses[0], axis=0) + batch_losses[1]
            )
            validation_batch_count += 1
        self.train_rmse.assign(self.train_rmse / validation_batch_count)
        self.train_rmse_m.assign(self.train_rmse_m / validation_batch_count)
        self.train_loss.assign(self.train_loss / validation_batch_count)

        # Same, but for the test data
        self.test_rmse.assign(tf.zeros([self.specification["nOutputChannels"]]))
        self.test_rmse_m.assign(tf.zeros([self.specification["nOutputChannels"]]))
        self.test_loss.assign(0.0)
        test_batch_count = 0
        for batch in testDS:
            # Metrics over masked area
            if (
                self.specification["trainingMask"] is not None
            ):  # Metrics over masked area
                mbatch = tf.where(
                    self.specification["trainingMask"] == 0, batch[-1], 0.0
                )
                per_replica_losses = self.specification["strategy"].run(
                    self.compute_loss, args=((batch[:-1], mbatch), False)
                )
                batch_losses = self.specification["strategy"].reduce(
                    tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
                )
                self.test_rmse_m.assign_add(batch_losses[0])
            # Metrics over unmasked area
            if self.specification["trainingMask"] is not None:
                mbatch = tf.where(
                    self.specification["trainingMask"] != 0, batch[-1], 0.0
                )
                batch = (batch[:-1], mbatch)
            per_replica_losses = self.specification["strategy"].run(
                self.compute_loss, args=(batch, False)
            )
            batch_losses = self.specification["strategy"].reduce(
                tf.distribute.ReduceOp.MEAN, per_replica_losses, axis=None
            )
            self.test_rmse.assign_add(batch_losses[0])
            self.regularization_loss.assign(batch_losses[1])
            self.test_loss.assign_add(
                tf.math.reduce_mean(batch_losses[0], axis=0) + batch_losses[1]
            )
            test_batch_count += 1
        self.test_rmse.assign(self.test_rmse / test_batch_count)
        self.test_rmse_m.assign(self.test_rmse / test_batch_count)
        self.test_loss.assign(self.test_loss / test_batch_count)

    # Save metrics to a log file
    def updateLogfile(self, logfile_writer, epoch):
        with logfile_writer.as_default():
            # For vector metrics like RMSE, log each component separately
            for i in range(self.specification["nOutputChannels"]):
                var_name = (
                    self.specification["outputNames"][i]
                    if hasattr(self.specification, "outputNames")
                    else f"var_{i}"
                )
                tf.summary.scalar(
                    f"Train_RMSE/{var_name}", self.train_rmse[i], step=epoch
                )
                tf.summary.scalar(
                    f"Test_RMSE/{var_name}", self.test_rmse[i], step=epoch
                )

                if self.specification["trainingMask"] is not None:
                    tf.summary.scalar(
                        f"Train_RMSE_masked/{var_name}",
                        self.train_rmse_m[i],
                        step=epoch,
                    )
                    tf.summary.scalar(
                        f"Test_RMSE_masked/{var_name}", self.test_rmse_m[i], step=epoch
                    )

            # Continue with scalar metrics
            tf.summary.scalar("Train_loss", self.train_loss, step=epoch)
            tf.summary.scalar("Test_loss", self.test_loss, step=epoch)
            tf.summary.scalar(
                "Regularization_loss", self.regularization_loss, step=epoch
            )
            logfile_writer.flush()

    # Print out the current metrics
    def printState(self):
        for i in range(self.specification["nOutputChannels"]):
            if self.specification["trainingMask"] is not None:
                print(
                    "{:<10s}: {:>9.3f}, {:>9.3f}, {:>9.3f}, {:>9.3f}".format(
                        self.specification["outputNames"][i],
                        self.train_rmse.numpy()[i],
                        self.test_rmse.numpy()[i],
                        self.train_rmse_m.numpy()[i],
                        self.test_rmse_m.numpy()[i],
                    )
                )
            else:
                print(
                    "{:<10s}: {:>9.3f}, {:>9.3f}".format(
                        self.specification["outputNames"][i],
                        self.train_rmse.numpy()[i],
                        self.test_rmse.numpy()[i],
                    )
                )
        print(
            "regularize:            {:>9.3f}".format(
                self.regularization_loss.numpy(),
            )
        )
        print(
            "loss      : {:>9.3f}, {:>9.3f}".format(
                self.train_loss.numpy(),
                self.test_loss.numpy(),
            )
        )

    sys.stdout.flush()


# Load model and initial weights
def getModel(specification, optimizer, epoch=1):
    # Instantiate the model
    # autoencoder = UNet(specification)

    class UNetLoader(tf.keras.Model):
        @classmethod
        def from_config(cls, config, custom_objects=None):
            return UNet(specification=specification, **config)

    # If Epoch is None - set it to latest saved value
    if epoch is None:
        try:
            weights_dir = ("%s/MLP/%s/weights") % (
                os.getenv("SCRATCH"),
                specification["modelName"],
            )
            # Find all the subdirectories in the weights directory
            subdirs = [
                os.path.join(weights_dir, d)
                for d in os.listdir(weights_dir)
                if os.path.isdir(os.path.join(weights_dir, d))
            ]
            # Sort the subdirectories by name (which includes the epoch number)
            subdirs.sort()
            # Get the latest subdirectory with
            latest_subdir = subdirs[
                -2
            ]  # not -1 because it might have died in the middle of saving
            # Get the epoch number from the subdirectory name
            epoch = int(os.path.basename(latest_subdir).split("_")[1])
            print("Continuing from epoch: %d" % epoch)
        except Exception as e:
            print("No saved weights found - starting from scratch")
            epoch = 1

    # If we are doing a restart, load the weights
    if epoch > 1:
        weights_dir = ("%s/MLP/%s/weights/Epoch_%04d") % (
            os.getenv("SCRATCH"),
            specification["modelName"],
            epoch,
        )
        autoencoder = tf.keras.models.load_model(
            "%s/ckpt.keras" % weights_dir,
            compile=True,
            custom_objects={"UNet": UNetLoader},
        )
    else:
        autoencoder = UNet(specification)
        autoencoder.compile(optimizer=optimizer)

    return (autoencoder, epoch)
