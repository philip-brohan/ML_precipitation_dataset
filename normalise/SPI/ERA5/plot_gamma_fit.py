#!/usr/bin/env python

# Plot maps of the three parameters in the gamma normalisation fit
#  shape, location, and scale.

import os
import iris
import numpy as np

from utilities import plots
from get_data.ERA5 import ERA5_monthly

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean

# Load the fitted values
shape = iris.load_cube("%s/MLP/normalisation/SPI/ERA5/shape.nc" % os.getenv("SCRATCH"))
ERA5_monthly.add_coord_system(shape)
location = iris.load_cube(
    "%s/MLP/normalisation/SPI/ERA5/location.nc" % os.getenv("SCRATCH")
)
ERA5_monthly.add_coord_system(location)
scale = iris.load_cube("%s/MLP/normalisation/SPI/ERA5/scale.nc" % os.getenv("SCRATCH"))
ERA5_monthly.add_coord_system(scale)

# Make the plot
fig = Figure(
    figsize=(10 * 3 / 2, 10),
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

ax_shape = fig.add_axes([0.05, 0.68, 0.9, 0.31])
plots.plotFieldAxes(
    ax_shape,
    shape,
    plotCube=plots.plot_cube(),
    vMin=np.percentile(shape.data.data, 5),
    vMax=np.percentile(shape.data.data, 95),
    cMap=cmocean.cm.rain,
)

ax_location = fig.add_axes([0.05, 0.34, 0.9, 0.31])
plots.plotFieldAxes(
    ax_location,
    location,
    plotCube=plots.plot_cube(),
    vMin=np.percentile(location.data.data, 5),
    vMax=np.percentile(location.data.data, 95),
    cMap=cmocean.cm.rain_r,
)

ax_scale = fig.add_axes([0.05, 0.01, 0.9, 0.31])
plots.plotFieldAxes(
    ax_scale,
    scale,
    plotCube=plots.plot_cube(),
    vMin=np.percentile(scale.data.data, 5),
    vMax=np.percentile(scale.data.data, 95),
    cMap=cmocean.cm.rain,
)

fig.savefig("gamma.png")
