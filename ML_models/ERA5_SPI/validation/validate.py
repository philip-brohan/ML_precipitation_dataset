#!/usr/bin/env python

# Plot a validation figure for the autoencoder.

# For normalised and unnormalised fields:
#  1) Input field
#  2) Autoencoder output
#  3) scatter plot
#

import os
import sys
import numpy as np
import tensorflow as tf
import iris
import iris.fileformats
import iris.analysis
import cmocean

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

sys.path.append("%s/.." % os.path.dirname(__file__))
from localise import ModelName

import warnings

warnings.filterwarnings("ignore", message=".*partition.*")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--epoch", help="Epoch", type=int, required=False, default=250)
parser.add_argument("--year", help="Test year", type=int, required=False, default=2004)
parser.add_argument("--month", help="Test month", type=int, required=False, default=12)
args = parser.parse_args()

from utilities import plots
from get_data import load_monthly

from autoencoderModel import DCVAE
from make_tensors.tensor_utils import (
    load_raw,
    raw_to_tensor,
    tensor_to_raw,
    normalise,
    unnormalise,
    sCube,
)


# Load and standardise data
qd = load_raw(args.year, args.month)
ic_source = raw_to_tensor(qd)

autoencoder = DCVAE()
weights_dir = "%s/MLP/%s/weights/Epoch_%04d" % (
    os.getenv("SCRATCH"),
    ModelName,
    args.epoch,
)
load_status = autoencoder.load_weights("%s/ckpt" % weights_dir)
# Check the load worked
load_status.assert_existing_objects_matched()

# Get autoencoded tensor
encoded = autoencoder.call(tf.reshape(ic_source, [1, 721, 1440, 1]), training=False)

# Make the plot
fig = Figure(
    figsize=(25, 11),
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
        facecolor=(1.0, 1.0, 1.0, 1),
        fill=True,
        zorder=1,
    )
)


# Top left - raw original
varx = qd.regrid(sCube, iris.analysis.Nearest())
(dmin, dmax) = (0, 0.03)
ax_ro = fig.add_axes([0.000 / 3, 0.125 / 2 + 0.5, 0.95 * 2 / 5, 0.85 / 2])
ax_ro.set_axis_off()
ro_img = plots.plotFieldAxes(
    ax_ro,
    varx,
    vMax=dmax,
    vMin=dmin,
    cMap=cmocean.cm.rain,
)
ax_ro_cb = fig.add_axes([0.10 / 3, 0.06 / 2 + 0.5, 0.75 * 2 / 5, 0.05 / 2])
ax_ro_cb.set_axis_off()
cb = fig.colorbar(
    ro_img, ax=ax_ro_cb, location="bottom", orientation="horizontal", fraction=1.0
)

# Top centre - raw encoded
vary = sCube.copy()
vary.data = np.squeeze(encoded[0, :, :, 0].numpy())
vary = unnormalise(vary)
ax_re = fig.add_axes(
    [0.000 / 3 + 2 / 5 - 0.02, 0.125 / 2 + 0.5, 0.95 * 2 / 5, 0.85 / 2]
)
ax_re.set_axis_off()
re_img = plots.plotFieldAxes(
    ax_re,
    vary,
    vMax=dmax,
    vMin=dmin,
    cMap=cmocean.cm.rain,
)
ax_re_cb = fig.add_axes(
    [0.100 / 3 + 2 / 5 - 0.02, 0.06 / 2 + 0.5, 0.75 * 2 / 5, 0.05 / 2]
)
ax_re_cb.set_axis_off()
cb = fig.colorbar(
    re_img,
    ax=ax_re_cb,
    location="bottom",
    orientation="horizontal",
    fraction=1.0,
)

# Top right - raw scatter
ax_rs = fig.add_axes([0.005 / 3 + 4 / 5, 0.125 / 2 + 0.5, 0.95 / 5, 0.85 / 2])
ax_rs.set_xticks([0.005, 0.015, 0.025])
ax_rs.set_yticks([0.0, 0.01, 0.02, 0.03])
vary.data[vary.data > dmax] = dmax  # Scatter plot fn can't cope with bad data
plots.plotScatterAxes(ax_rs, varx, vary, vMin=dmin, vMax=dmax, bins="log")

# Bottom left - normalised original
varx.data = np.squeeze(ic_source.numpy())
(dmin, dmax) = (-0.25, 1.25)
ax_no = fig.add_axes([0.000 / 3, 0.125 / 2, 0.95 * 2 / 5, 0.85 / 2])
ax_no.set_axis_off()
no_img = plots.plotFieldAxes(
    ax_no,
    varx,
    vMax=dmax,
    vMin=dmin,
    cMap=cmocean.cm.rain,
)
ax_no_cb = fig.add_axes([0.10 / 3, 0.06 / 2, 0.75 * 2 / 5, 0.05 / 2])
ax_no_cb.set_axis_off()
cb = fig.colorbar(
    no_img, ax=ax_no_cb, location="bottom", orientation="horizontal", fraction=1.0
)

# Bottom centre - normalised encoded
vary.data = encoded.numpy()[0, :, :, 0]
ax_ne = fig.add_axes([0.000 / 3 + 2 / 5 - 0.02, 0.125 / 2, 0.95 * 2 / 5, 0.85 / 2])
ax_ne.set_axis_off()
ne_img = plots.plotFieldAxes(
    ax_ne,
    vary,
    vMax=dmax,
    vMin=dmin,
    cMap=cmocean.cm.rain,
)
ax_ne_cb = fig.add_axes([0.1 / 3 + 2 / 5 - 0.02, 0.06 / 2, 0.75 * 2 / 5, 0.05 / 2])
ax_ne_cb.set_axis_off()
cb = fig.colorbar(
    ne_img, ax=ax_ne_cb, location="bottom", orientation="horizontal", fraction=1.0
)

# Bottom right - normalised scatter
ax_ns = fig.add_axes([0.005 / 3 + 4 / 5, 0.125 / 2, 0.95 / 5, 0.85 / 2])
plots.plotScatterAxes(ax_ns, varx, vary, vMin=dmin, vMax=dmax, bins="log")


fig.savefig("comparison.png")
