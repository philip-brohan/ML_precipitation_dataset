# Custom TF model for gamma distribution fitting

import tensorflow as tf
import tensorflow_probability as tfp

# Relative scaling factors for losses
fit_scale = 1.0
shape_regularization_factor = 0.0
scale_regularization_factor = 0.01
location_regularization_factor = 0.01
shape_neighbour_factor = 0.0
scale_neighbour_factor = 0.0
location_neighbour_factor = 0.0


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
            initializer=tf.keras.initializers.Constant(value=100.0*5),
            trainable=True,
            name="shape",
        )
        self.location = self.add_weight(
            shape=input_shape[1:],
            initializer=tf.keras.initializers.Constant(value=200.0),
            trainable=True,
            name="location",
        )
        self.scale = self.add_weight(
            shape=input_shape[1:],
            initializer=tf.keras.initializers.Constant(value=10.0*10),
            trainable=True,
            name="scale",
        )

    def call(self, inputs):
        # Constrain scale and shape to be +ve
        dists = tfp.distributions.Gamma(
            concentration=tf.nn.relu(self.scale/5)+0.001, rate=1.0 / (tf.nn.relu(self.shape/10)+0.1)
        )
        #dists = tfp.distributions.Normal(
        #    self.location, tf.nn.relu(self.scale/10)+0.01
        #)
        # Regularize
        self.add_loss(
            shape_regularization_factor * tf.reduce_mean(tf.square(self.shape))
        )
        self.add_loss(
            scale_regularization_factor * tf.reduce_mean(tf.square(self.scale))
        )
        self.add_loss(
            location_regularization_factor * tf.reduce_mean(tf.square(self.location))
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
        return dists.log_prob(inputs-self.location)*-1
        #return tf.reduce_mean(tf.math.squared_difference(inputs,self.location))


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
