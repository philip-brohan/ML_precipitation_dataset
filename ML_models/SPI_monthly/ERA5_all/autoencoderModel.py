# Specify a Deep Convolutional Variational AutoEncoder
#  Take the input structure from specify.py

import tensorflow as tf

import specify


class DCVAE(tf.keras.Model):
    # Initialiser - set up instance and define the models
    def __init__(self):
        super(DCVAE, self).__init__()

        # Model to encode input to latent space distribution
        self.encoder = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(
                    input_shape=(721, 1440, specify.nInputChannels)
                ),
                tf.keras.layers.Conv2D(
                    filters=5,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Conv2D(
                    filters=10,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Conv2D(
                    filters=10,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Conv2D(
                    filters=20,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Conv2D(
                    filters=40,
                    kernel_size=3,
                    strides=(2, 2),
                    padding="same",
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Flatten(),
                # No activation
                tf.keras.layers.Dense(
                    specify.latentDimension + specify.latentDimension,
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
            ]
        )

        # Model to generate output from latent space
        self.generator = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(input_shape=(specify.latentDimension,)),
                tf.keras.layers.Dense(
                    units=23 * 45 * 40,
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Reshape(target_shape=(23, 45, 40)),
                tf.keras.layers.Conv2DTranspose(
                    filters=20,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(1, 1),
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Conv2DTranspose(
                    filters=10,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(0, 1),
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Conv2DTranspose(
                    filters=10,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(0, 1),
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Conv2DTranspose(
                    filters=5,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(0, 1),
                    activation="elu",
                    kernel_regularizer=tf.keras.regularizers.L2(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01),
                ),
                tf.keras.layers.Conv2DTranspose(
                    filters=specify.nOutputChannels,
                    kernel_size=3,
                    strides=2,
                    padding="same",
                    output_padding=(0, 1),
                ),
            ]
        )

    # Call the encoder model with a batch of input examples and return a batch of
    #  means and a batch of variances of the encoded latent space PDFs.
    def encode(self, x, training=False):
        mean, logvar = tf.split(
            self.encoder(x, training=training), num_or_size_splits=2, axis=1
        )
        return mean, logvar

    # Sample a batch of points in latent space from the encoded means and variances
    def reparameterize(self, mean, logvar, training=False):
        eps = tf.random.normal(shape=mean.shape)
        return eps * tf.exp(logvar * 0.5) + mean

    # Call the generator model with a batch of points in latent space and return a
    #  batch of outputs
    def generate(self, z, training=False):
        generated = self.generator(z, training=training)
        return generated

    # Run the full VAE - convert a batch of inputs to one of outputs
    def call(self, x, training=True):
        mean, logvar = self.encode(x, training=training)
        latent = self.reparameterize(mean, logvar, training=training)
        generated = self.generate(latent, training=training)
        return generated

    # Utility function to calculte fit of sample to N(mean,logvar)
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
        mean, logvar = self.encode(x[0], training=training)
        latent = self.reparameterize(mean, logvar, training=training)
        generated = self.generate(latent, training=training)

        gV = generated
        cV = gV * 0.0 + 0.5  # Climatology
        tV = x[0]
        fit_metric = self.fit_loss(gV, tV, cV)

        logpz = (
            tf.reduce_mean(self.log_normal_pdf(latent, 0.0, 0.0) * -1) * specify.beta
        )
        logqz_x = (
            tf.reduce_mean(self.log_normal_pdf(latent, mean, logvar)) * specify.beta
        )

        return (
            fit_metric,
            logpz,
            logqz_x,
        )

    # Run the autoencoder for one batch, calculate the errors, calculate the
    #  gradients and update the layer weights.
    @tf.function
    def train_on_batch(self, x, optimizer):
        with tf.GradientTape() as tape:
            loss_values = self.compute_loss(x, training=True)
            overall_loss = (
                tf.math.reduce_sum(loss_values[0], axis=0)  # RMSE
                + loss_values[1]  # logpz
                + loss_values[2]  # logqz_x
                + tf.add_n(self.losses)  # Regularization
            )
        gradients = tape.gradient(overall_loss, self.trainable_variables)
        # Clip the gradients - helps against sudden numerical problems
        if specify.maxGradient is not None:
            gradients = [tf.clip_by_norm(g, specify.maxGradient) for g in gradients]
        optimizer.apply_gradients(zip(gradients, self.trainable_variables))
