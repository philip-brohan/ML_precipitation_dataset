# Use the trained gamma fit to make normalized data
# The aim is to make a normalized distribution that is normally distributed
#  with mean=0.5 and sd=0.2 (so almost all the data is in 0-1)
import numpy as np

import os
import iris
from get_data.TWCR import TWCR_monthly_load

import tensorflow as tf
import tensorflow_probability as tfp
from fitterModel import Gamma_Fitter, GammaC

from make_tensors.tensor_utils import raw_to_tensor, tensor_to_cube

ndist = tfp.distributions.Normal(loc=0.5, scale=0.2)
nLayer = GammaC()


# Load the pre-calculated fitted model
def load_fitted(month, variable="PRATE", epoch=250):
    # Load the trained model - params are its weights
    fitter = Gamma_Fitter(nLayer)
    weights_dir = "%s/MLP/fitter/TWCR/%s/%02d/weights/Epoch_%04d" % (
        os.getenv("SCRATCH"),
        variable,
        month,
        epoch,
    )
    load_status = fitter.load_weights("%s/ckpt" % weights_dir)
    load_status.assert_existing_objects_matched()

    return fitter


# Normalise an input cube (given a fitted model)
def normalize_cube(raw, model):
    input = raw_to_tensor(raw)
    input = tf.reshape(input, [721, 1440, 1])
    gl = model.get_layer("sequential").get_layer("gamma_c")
    normalized = gl.normalize(input)
    normalized = tf.reshape(normalized, [721, 1440])
    return tensor_to_cube(normalized)
