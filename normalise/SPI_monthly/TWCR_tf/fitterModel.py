# Custom TF model for gamma distribution fitting

import sys
import tensorflow as tf
import tensorflow_probability as tfp


# Class to initialize weights to a given tensor
class ToTensor(tf.keras.initializers.Initializer):
    def __init__(self, values):
        self.values = values

    def __call__(self, shape, dtype=None):
        return tf.Variable(self.values)


# Define a TF layer to compare its input against a gamma distribution
# Returns the probability of the inputs given a gamma distribution
#  defined by the layer weights. (Train weights to maximise this).
class GammaC(
    tf.keras.layers.Layer,
):
    def __init__(
        self,
        fg_shape=tf.zeros([721, 1440, 1], tf.float32),
        fg_location=tf.zeros([721, 1440, 1], tf.float32),
        fg_scale=tf.zeros([721, 1440, 1], tf.float32),
        fit_loss_scale=1.0,
        shape_regularization_factor=0.0,
        scale_regularization_factor=0.0,
        location_regularization_factor=0.0,
        shape_neighbour_factor=0.0,
        scale_neighbour_factor=0.0,
        location_neighbour_factor=0.0,
        train_location=False,
        train_scale=True,
        train_shape=True,
    ):
        super().__init__()
        self.fg_shape = fg_shape
        self.fg_location = fg_location
        self.fg_scale = fg_scale
        self.fit_loss_scale = fit_loss_scale
        self.shape_regularization_factor = shape_regularization_factor
        self.scale_regularization_factor = scale_regularization_factor
        self.location_regularization_factor = location_regularization_factor
        self.shape_neighbour_factor = shape_neighbour_factor
        self.scale_neighbour_factor = scale_neighbour_factor
        self.location_neighbour_factor = location_neighbour_factor
        self.train_location = train_location
        self.train_scale = train_scale
        self.train_shape = train_shape

        # Normal dist for normalization functions
        self.ndist = tfp.distributions.Normal(loc=0.5, scale=0.2)

    def build(self, input_shape):
        self.shape = self.add_weight(
            shape=input_shape[1:],
            initializer=ToTensor(self.fg_shape),
            trainable=self.train_shape,
            name="shape",
        )
        self.location = self.add_weight(
            shape=input_shape[1:],
            initializer=ToTensor(self.fg_location),
            trainable=self.train_location,
            name="location",
        )
        self.scale = self.add_weight(
            shape=input_shape[1:],
            initializer=ToTensor(self.fg_scale),
            trainable=self.train_scale,
            name="scale",
        )

    def call(self, inputs):
        # Constrain scale and shape to be +ve
        tf.debugging.check_numerics(self.location, "Bad location")
        tf.debugging.check_numerics(self.scale, "Bad scale")
        tf.debugging.check_numerics(self.shape, "Bad shape")
        dists = tfp.distributions.Gamma(
            concentration=tf.nn.relu(self.shape) + self.fg_shape / 100,
            rate=1.0 / (tf.nn.relu(self.scale) + self.fg_scale / 100),
        )
        # Regularize
        self.add_loss(
            self.shape_regularization_factor * tf.reduce_mean(tf.square(self.shape))
        )
        self.add_loss(
            self.scale_regularization_factor * tf.reduce_mean(tf.square(self.scale))
        )
        self.add_loss(
            self.location_regularization_factor
            * tf.reduce_mean(tf.square(self.location))
        )
        self.add_loss(
            self.shape_neighbour_factor
            * (
                tf.reduce_mean(tf.square(self.shape[1:, :] - self.shape[:-1, :]))
                + tf.reduce_mean(tf.square(self.shape[:, 1:] - self.shape[:, :-1]))
            )
        )
        self.add_loss(
            self.scale_neighbour_factor
            * (
                tf.reduce_mean(tf.square(self.scale[1:, :] - self.scale[:-1, :]))
                + tf.reduce_mean(tf.square(self.scale[:, 1:] - self.scale[:, :-1]))
            )
        )
        self.add_loss(
            self.location_neighbour_factor
            * (
                tf.reduce_mean(tf.square(self.location[1:, :] - self.location[:-1, :]))
                + tf.reduce_mean(
                    tf.square(self.location[:, 1:] - self.location[:, :-1])
                )
            )
        )
        loc_off = tf.nn.relu(self.fg_location - self.location)
        lp = dists.log_prob(inputs - self.location + loc_off)
        # tf.print(tf.where(tf.math.is_nan(lp)))
        # tf.debugging.check_numerics(lp,"Bad probabilities")
        return lp * -1

    # Functions to be called to do normalisation
    def normalise(self, inputs):
        gdist = tfp.distributions.Gamma(
            concentration=tf.nn.relu(self.shape) + self.fg_shape / 100,
            rate=1.0 / (tf.nn.relu(self.scale) + self.fg_scale / 100),
        )
        cumul = gdist.cdf(inputs - self.location)
        cumul = tf.math.maximum(cumul, 0.0001)
        cumul = tf.math.minimum(cumul, 0.9999)
        return self.ndist.quantile(cumul)

    def unnormalise(self, inputs):
        gdist = tfp.distributions.Gamma(
            concentration=tf.nn.relu(self.shape) + self.fg_shape / 100,
            rate=1.0 / (tf.nn.relu(self.scale) + self.fg_scale / 100),
        )
        cumul = self.ndist.cdf(inputs)
        return gdist.quantile(cumul) + self.location


# Define the model
class Gamma_Fitter(tf.keras.Model):
    # Initialiser - set up instance and define the models
    def __init__(self, FitLayer):
        super(Gamma_Fitter, self).__init__()

        # Hyperparameters
        # Max gradient to apply in optimizer
        self.max_gradient = 2.0

        # Model to encode input to latent space distribution
        self.fitter = tf.keras.Sequential(
            [tf.keras.layers.InputLayer(input_shape=(721, 1440, 1)), FitLayer]
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
