# Model utility functions

import os
import numpy as np

import tensorflow as tf
from tensorflow.core.util import event_pb2
from tensorflow.python.framework import tensor_util

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

import cmocean

from utilities import plots, grids


# Convenience function to make everything a list
# lists stay lists, scalars become len=1 lists.
def listify(input):
    if isinstance(input, str):
        input = [input]
    else:
        try:
            iter(input)
        except TypeError:
            input = [input]
        else:
            input = list(input)
    return input


# Load the history of a model from the Tensorboard logs
def loadHistory(LSC, offset=-1, max_epoch=None):
    history = {}
    summary_dir = "%s/MLP/%s/logs/Training" % (os.getenv("SCRATCH"), LSC)
    Rfiles = os.listdir(summary_dir)
    Rfiles.sort(key=lambda x: os.path.getmtime(os.path.join(summary_dir, x)))
    filename = Rfiles[offset]
    path = os.path.join(summary_dir, filename)
    serialized_records = tf.data.TFRecordDataset(path)
    for srecord in serialized_records:
        event = event_pb2.Event.FromString(srecord.numpy())
        for value in event.summary.value:
            t = tensor_util.MakeNdarray(value.tensor)
            if not value.tag in history.keys():
                history[value.tag] = []
            if value.tag == "OutputNames":
                history[value.tag] = t
                continue
            if len(history[value.tag]) < event.step + 1:
                history[value.tag].extend(
                    [0.0] * (event.step + 1 - len(history[value.tag]))
                )
            history[value.tag][event.step] = t

    ymax = 0
    ymin = 1000000
    hts = {}
    n_epochs = len(history["Train_loss"])
    if max_epoch is not None:
        n_epochs = min(max_epoch, n_epochs)
    hts["epoch"] = list(range(n_epochs))[1:]
    for key in history:
        if key == "OutputNames":
            hts[key] = [str(t, "utf-8") for t in history[key]]
        else:
            hts[key] = [abs(t) for t in history[key][1:n_epochs]]
    for key in ("Train_logpz", "Train_logqz_x", "Test_logpz", "Test_logqz_x"):
        ymax = max(ymax, max(hts[key]))
        ymin = min(ymin, min(hts[key]))

    return (hts, ymax, ymin, n_epochs)


# Choose colourmap based on variable name
def get_cmap(name):
    if name == "PRATE" or name == "Precip":
        return cmocean.cm.tarn
    elif name == "MSLP":
        return cmocean.cm.diff
    else:
        return cmocean.cm.balance


# Plot a single-field validation figure for the autoencoder.
def plotValidationField(specification, input, output, year, month, fileName):
    nFields = specification["nOutputChannels"]

    # Make the plot
    figScale = 3.0
    wRatios = (2, 2, 1.25)
    fig = Figure(
        figsize=(figScale * sum(wRatios), figScale * nFields),
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
        "size": 12,
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

    # Each variable a row in it's own subfigure
    subfigs = fig.subfigures(nFields, 1, wspace=0.01)

    for varI in range(nFields):
        ax_var = subfigs[varI].subplots(nrows=1, ncols=3, width_ratios=wRatios)
        # Left - map of target
        varx = grids.E5sCube.copy()
        varx.data = np.squeeze(input[-1][:, :, :, varI].numpy())
        varx.data = np.ma.masked_where(varx.data == 0.0, varx.data, copy=False)
        if varI == 0:
            ax_var[0].set_title("%04d-%02d" % (year, month))
        ax_var[0].set_axis_off()
        x_img = plots.plotFieldAxes(
            ax_var[0],
            varx,
            vMax=1.25,
            vMin=-0.25,
            cMap=get_cmap(specification["outputNames"][varI]),
        )
        # Centre - map of model output
        vary = grids.E5sCube.copy()
        vary.data = np.squeeze(output[:, :, :, varI].numpy())
        vary.data = np.ma.masked_where(varx.data == 0.0, vary.data, copy=False)
        ax_var[1].set_axis_off()
        ax_var[1].set_title(specification["outputNames"][varI])
        x_img = plots.plotFieldAxes(
            ax_var[1],
            vary,
            vMax=1.25,
            vMin=-0.25,
            cMap=get_cmap(specification["outputNames"][varI]),
        )
        # Right - scatter plot of input::output
        ax_var[2].set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax_var[2].set_yticks([0, 0.25, 0.5, 0.75, 1])
        plots.plotScatterAxes(ax_var[2], varx, vary, vMin=-0.25, vMax=1.25, bins="log")

    fig.savefig(fileName)


def plotTrainingMetrics(
    hts, fileName="training.webp", chts=None, aymax=None, epoch=None
):
    fig = Figure(
        figsize=(15, 5),
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
        "size": 12,
    }
    matplotlib.rc("font", **font)

    # Plain background
    axb = fig.add_axes([0, 0, 1, 1])
    axb.set_axis_off()
    axb.add_patch(
        Rectangle(
            (0, 0),
            1,
            1,
            facecolor=(0.95, 0.0, 0.0, 1),
            fill=True,
            zorder=1,
        )
    )

    def addLine(ax, dta, key, col, z, idx=0, rscale=1):
        dtp = [listify(x)[idx] for x in dta[key] if len(listify(x)) > idx]
        dta2 = [
            dta["epoch"][i]
            for i in range(len(dta[key]))
            if len(listify(dta[key][i])) > idx
        ]
        ax.add_line(
            Line2D(
                dta2,
                np.array(dtp) * rscale,
                linewidth=2,
                color=col,
                alpha=1.0,
                zorder=z,
            )
        )

    # Three subfigures
    # Left - for the overall loss
    # Centre, for the RMS components
    # Right, for the KL-divergence components
    subfigs = fig.subfigures(1, 3, wspace=0.07)

    # Left - Main loss
    ymaxL = max(1, max(hts["Train_loss"] + hts["Test_loss"]))
    if chts is not None:
        ymaxL = max(ymaxL, max(chts["Train_loss"] + chts["Test_loss"]))
    if aymax is not None:
        ymaxL = aymax
    subfigs[0].subplots_adjust(left=0.2)
    ax_loss = subfigs[0].subplots(nrows=1, ncols=1)
    ax_loss.set_xlim(left=-1, right=epoch + 1, auto=False)
    ax_loss.set_ylim(bottom=0, top=ymaxL, auto=False)
    ax_loss.set_ylabel("Overall loss")
    ax_loss.set_xlabel("epoch")
    ax_loss.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)

    addLine(ax_loss, hts, "Train_loss", (1, 0.5, 0.5, 1), 10)
    addLine(ax_loss, hts, "Test_loss", (1, 0, 0, 1), 20)
    if chts is not None:
        addLine(ax_loss, chts, "Train_loss", (0.5, 0.5, 1, 1), 10)
        addLine(ax_loss, chts, "Test_loss", (0, 0, 1, 1), 20)

    # Centre, plot each RMS component as a separate subplot.
    comp_font_size = 10
    nvar = len(hts["OutputNames"])
    # Layout n plots in an (a,b) grid
    try:
        subplotLayout = [
            None,
            (1, 1),
            (1, 2),
            (2, 2),
            (2, 2),
            (2, 3),
            (2, 3),
            (3, 3),
            (3, 3),
            (3, 3),
        ][nvar + 1]
    except Exception:
        raise Exception("No subplot layout for %d plots" % nvar)
    if subplotLayout is None:
        raise Exception("No output names found")
    ax_rmse = subfigs[1].subplots(
        nrows=subplotLayout[0],
        ncols=subplotLayout[1],
        sharex=True,
        sharey=True,
    )
    ax_rmse = [item for row in ax_rmse for item in row]  # Flatten
    ax_rmse[0].set_xlim(-1, epoch + 1)
    ax_rmse[0].set_ylim(0, ymaxL)
    ax_rmse[0].set_ylabel("Variance fraction", fontsize=comp_font_size)
    ax_rmse[nvar].set_xlabel("Epoch", fontsize=comp_font_size)
    for varI in range(nvar):
        ax_rmse[varI].tick_params(axis="both", labelsize=comp_font_size)
        ax_rmse[varI].set_title(hts["OutputNames"][varI], fontsize=comp_font_size)
        ax_rmse[varI].grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
        addLine(ax_rmse[varI], hts, "Train_RMSE", (1, 0.5, 0.5, 1), 10, idx=varI)
        addLine(ax_rmse[varI], hts, "Test_RMSE", (1, 0, 0, 1), 20, idx=varI)
    ax_rmse[nvar].tick_params(axis="both", labelsize=comp_font_size)
    ax_rmse[nvar].set_title("Regularization", fontsize=comp_font_size)
    ax_rmse[nvar].grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
    addLine(ax_rmse[nvar], hts, "Regularization_loss", (1, 0, 0, 1), 20)
    for varI in range(nvar + 1, len(ax_rmse)):
        ax_rmse[varI].set_axis_off()

    # Right - KL-divergence plots
    ax_kld = subfigs[2].subplots(
        nrows=2,
        ncols=1,
        sharex=True,
        sharey=False,
    )
    ax_kld[0].set_xlim(-1, epoch + 1)
    ymaxL = max(hts["Train_logpz"] + hts["Test_logpz"])
    yminL = min(hts["Train_logpz"] + hts["Test_logpz"])
    if chts is not None:
        ymaxL = max(ymaxL, max(chts["Train_logpz"] + chts["Test_logpz"]))
        yminL = min(yminL, min(chts["Train_logpz"] + chts["Test_logpz"]))
    ymaxL += (ymaxL - yminL) / 20
    yminL -= (ymaxL - yminL) / 21
    ax_kld[0].set_ylim(yminL, ymaxL)
    ax_kld[0].set_title("KL Divergence")
    ax_kld[0].set_ylabel("logpz")
    ax_kld[0].set_xlabel("")
    ax_kld[0].grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
    addLine(ax_kld[0], hts, "Train_logpz", (1, 0.5, 0.5, 1), 10)
    addLine(ax_kld[0], hts, "Test_logpz", (1, 0, 0, 1), 20)
    if chts is not None:
        addLine(ax_kld[0], chts, "Train_logpz", (0.5, 0.5, 1, 1), 10)
        addLine(ax_kld[0], chts, "Test_logpz", (0, 0, 1, 1), 20)

    ymaxL = max(hts["Train_logqz_x"] + hts["Test_logqz_x"])
    yminL = min(hts["Train_logqz_x"] + hts["Test_logqz_x"])
    if chts is not None:
        ymaxL = max(ymaxL, max(chts["Train_logqz_x"] + chts["Test_logqz_x"]))
        yminL = min(yminL, min(chts["Train_logqz_x"] + chts["Test_logqz_x"]))
    ymaxL += (ymaxL - yminL) / 20
    yminL -= (ymaxL - yminL) / 21
    ax_kld[1].set_ylim(yminL, ymaxL)
    ax_kld[1].set_ylabel("logqz_x")
    ax_kld[1].set_xlabel("epoch")
    ax_kld[1].grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
    addLine(ax_kld[1], hts, "Train_logqz_x", (1, 0.5, 0.5, 1), 10)
    addLine(ax_kld[1], hts, "Test_logqz_x", (1, 0, 0, 1), 20)
    if chts is not None:
        addLine(ax_kld[1], chts, "Train_logqz_x", (0.5, 0.5, 1, 1), 10)
        addLine(ax_kld[1], chts, "Test_logqz_x", (0, 0, 1, 1), 20)

    # Output as png
    fig.savefig(fileName)
