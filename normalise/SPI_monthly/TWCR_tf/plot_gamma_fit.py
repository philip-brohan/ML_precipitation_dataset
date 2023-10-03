#!/usr/bin/env python

# Plot maps of the three parameters in the gamma normalisation fit
# For a specified month - shape, location, and scale.

import os
import iris
import sys
import iris.time
import iris.util
import numpy as np

from utilities import plots
from utilities import grids

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean
import argparse

import tensorflow as tf

from fitterModel import Gamma_Fitter


parser = argparse.ArgumentParser()
parser.add_argument(
    "--month", help="Month to plot", type=int, required=False, default=3
)
parser.add_argument(
    "--epoch", help="Epoch to plot", type=int, required=False, default=1
)
parser.add_argument(
    "--variable",
    help="Name of variable to use (PRATE, TMP2m, PRMSL, ...)",
    type=str,
    default="PRATE",
)
args = parser.parse_args()

# Load the trained model - params are its weights
fitter = Gamma_Fitter()
weights_dir = "%s/MLP/fitter/%s/weights/Epoch_%04d" % (
    os.getenv("SCRATCH"),
    args.variable,
    args.epoch,
)
load_status = fitter.load_weights("%s/ckpt" % weights_dir)
load_status.assert_existing_objects_matched()

# Turn the weight parameters into cubes
gl = fitter.get_layer('sequential').get_layer('gamma_c')
shape = grids.E5sCube.copy()
for weight in gl.weights:
    if weight.name == 'gamma_c/shape:0':
        shape.data = np.squeeze(weight.numpy())
location = grids.E5sCube.copy()
for weight in gl.weights:
    if weight.name == 'gamma_c/location:0':
        location.data = np.squeeze(weight.numpy())
scale = grids.E5sCube.copy()
for weight in gl.weights:
    if weight.name == 'gamma_c/scale:0':
        scale.data = np.squeeze(weight.numpy())

# Make the plot
fig = Figure(
    figsize=(10, 10 * 3 / 2),
    dpi=100,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
    subplotpars=None,
    tight_layout=None,
)
canvas = FigureCanvas(fig)
font = {
    "family": "sans-serif",
    "sans-serif": "Arial",
    "weight": "normal",
    "size": 20,
}
matplotlib.rc("font", **font)
axb = fig.add_axes([0, 0, 1, 1])
axb.set_axis_off()
axb.add_patch(
    Rectangle(
        (0, 0),
        1,
        1,
        facecolor=(1.0, 0.0, 0.0, 1),
        fill=True,
        zorder=1,
    )
)

ax_shape = fig.add_axes([0.05, 0.68, 0.9, 0.31])
plots.plotFieldAxes(
    ax_shape,
    shape,
    #vMin=np.percentile(shape.data.data, 0.05),
    #vMax=np.percentile(shape.data.data, 99.95),
    cMap=cmocean.cm.balance,
)

ax_location = fig.add_axes([0.05, 0.345, 0.9, 0.31])
plots.plotFieldAxes(
    ax_location,
    location,
    #vMin=np.percentile(location.data.data, 0.055),
    #vMax=np.percentile(location.data.data, 99.95),
    cMap=cmocean.cm.balance,
)

ax_scale = fig.add_axes([0.05, 0.01, 0.9, 0.31])
plots.plotFieldAxes(
    ax_scale,
    scale,
    #vMin=np.percentile(scale.data.data, 0.05),
    #vMax=np.percentile(scale.data.data, 99.95),
    cMap=cmocean.cm.balance,
)

fig.savefig("gamma.png")
