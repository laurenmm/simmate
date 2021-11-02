# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------

import numpy

from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import Pathway as Pathway_DB

queryset = (
    Pathway_DB.objects.filter(
        vaspcalca__energy_barrier__isnull=False,
        vaspcalca__energy_barrier__gte=0,
        empiricalmeasures__ionic_radii_overlap_anions__gt=-900,
        # empiricalmeasuresb__ewald_energyb__gte=6,
        # empiricalmeasuresb__ewald_energyb__lte=100,
        length__gte=4.25,
        # length__lte=4.75,
    )
    .select_related("vaspcalca", "empiricalmeasuresb", "empcorbarrier")
    .all()
)
from django_pandas.io import read_frame

df = read_frame(
    queryset,
    fieldnames=[
        "length",
        "empiricalmeasuresb__ewald_energyb",
        "empiricalmeasures__ionic_radii_overlap_anions",
        "empiricalmeasures__ionic_radii_overlap_cations",
        "vaspcalca__energy_barrier",
        "empcorbarrier__barrier",
    ],
)

# --------------------------------------------------------------------------------------


# The code below is for interactive plotting using Plotly
# import plotly.express as px

# fig = px.scatter(
#     data_frame=df,
#     x="empiricalmeasures__ionic_radii_overlap_anions",
#     y="empiricalmeasures__ionic_radii_overlap_cations",
#     color="vaspcalca__energy_barrier",
#     range_color=[0, 5],
# )
# fig.show(renderer="browser", config={'scrollZoom': True})

# --------------------------------------------------------------------------------------


import matplotlib.pyplot as plt

# start with a square Figure
fig = plt.figure(figsize=(8, 8))

# Add a gridspec (which sets up a total of 4 subplots for us -- and we use 3)
gs = fig.add_gridspec(
    # grid dimensions and column/row relative sizes
    nrows=2,
    ncols=2,
    width_ratios=(7, 2),
    height_ratios=(2, 7),
    #
    # size of the overall grid (all axes together)
    left=0.1,   
    right=0.9,
    bottom=0.1,
    top=0.9,
    #
    # spacing between subplots (axes)
    wspace=0.05,
    hspace=0.05,
)

# HEXBIN SUBPLOT
# create the axes object
ax = fig.add_subplot(
    gs[1, 0],  # bottom left subplot
    xlabel=r"$\Delta$ Anion Overlap ($\AA$)",
    ylabel=r"$\Delta$ Cation Overlap ($\AA$)",
    facecolor="lightgrey",  # background color
)
# add dashed lines at x=0 and y=0
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
# create the hexbin subplot
hb = ax.hexbin(
    x=df["empiricalmeasures__ionic_radii_overlap_anions"],  # X
    y=df["empiricalmeasures__ionic_radii_overlap_cations"],  # Y
    C=df["empcorbarrier__barrier"],  # COLOR
    gridsize=40,  # size of hex bins
    cmap="RdYlGn_r",  # color scheme for colorbar
    vmin=0,
    vmax=1.5,  # upper limit of colorbar
    edgecolor="black",  # color between hex bins
    reduce_C_function=numpy.std,
    mincnt=5,
    extent=(-3, 3, -3, 3)
)
ax.set_xlim(-1.1,2.2)
ax.set_ylim(-2.2,1.5)
# add the colorbar (for positioning we give it its own axes)
# where arg is [left, bottom, width, height]
cax = fig.add_axes([0.33, 0.16, 0.35, 0.03])
cb = fig.colorbar(
    hb,  # links color to hexbin
    cax=cax,  # links location to this axes
    orientation="horizontal",
    label="Energy Barrier (eV)",
)

# X-AXIS HISTOGRAM
ax_histx = fig.add_subplot(
    gs[0, 0],  # top left subplot
    sharex=ax,
    ylabel="Pathways (#)",
    # facecolor="lightgrey",  # background color
)
ax_histx.hist(
    x=df["empiricalmeasures__ionic_radii_overlap_anions"],
    bins=75,
    color="black",
    edgecolor="white",
    linewidth=0.5,
)
ax_histx.axvline(0, color="black", linewidth=0.8, linestyle="--")

# Y-AXIS HISTOGRAM
ax_histy = fig.add_subplot(
    gs[1, 1],  # bottom right subplot
    sharey=ax,
    xlabel="Pathways (#)",
    # facecolor="lightgrey",  # background color
)
ax_histy.hist(
    x=df["empiricalmeasures__ionic_radii_overlap_cations"],
    orientation="horizontal",
    bins=75,
    color="black",
    edgecolor="white",
    linewidth=0.5,
)
ax_histy.axhline(0, color="black", linewidth=0.8, linestyle="--")

# setting subplot(xticklabels=[],) above doesn't work as intended so I do this here
ax_histx.tick_params(axis="x", labelbottom=False)
ax_histy.tick_params(axis="y", labelleft=False)

plt.show()
# plt.savefig("iro.svg", format="svg")

# --------------------------------------------------------------------------------------
