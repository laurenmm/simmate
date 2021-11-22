# -*- coding: utf-8 -*-

import matplotlib

font = {"family": "normal", "weight": "normal", "size": 16}

matplotlib.rc("font", **font)

# --------------------------------------------------------------------------------------

import numpy

from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import Pathway as Pathway_DB

queryset = (
    Pathway_DB.objects.filter(
        vaspcalca__energy_barrier__isnull=False,
        # vaspcalca__energy_barrier__gte=0,
        # empiricalmeasures__ionic_radii_overlap_anions__gt=-900,
        # structure__prototype2__formula_reduced="Ba2MnWO6",
        # structure__prototype2__name="(Cubic) Perovskite",
        # structure__prototype3__number=22,
    ).select_related(
        "vaspcalca", "empiricalmeasures", "empiricalmeasuresb", "empcorbarrier"
    )
    # .distinct("structure")
    .all()
)
from django_pandas.io import read_frame

df = read_frame(
    queryset,
    fieldnames=[
        "length",
        "empiricalmeasures__ewald_energy",
        "empiricalmeasures__ionic_radii_overlap_anions",
        "empiricalmeasures__ionic_radii_overlap_cations",
        "vaspcalca__energy_barrier",
        "empcorbarrier__barrier",
        "empiricalmeasuresb__ewald_energyb",
        # "vaspcalcb__energy_barrier",
        "structure__prototype3__number",
        "structure__prototype2__formula_reduced",
        "structure__prototype2__name",
        "structure__formula_reduced",
        "structure__formula_anonymous",
        "structure__spacegroup",
        "structure__id",
    ],
)

# --------------------------------------------------------------------------------------


def add_scatter_and_trendline(
    ax, df, field, color="green", hist_bins=None, hist_range=None
):

    # ----------

    # add the data as a scatter
    scatter = ax.scatter(
        x=df[field],  # X
        y=df["empcorbarrier__barrier"],  # Y
        c=color,
        alpha=0.25,
    )

    # ----------

    # add hist trend line
    _, divisions = numpy.histogram(
        df[field],
        bins=hist_bins,
        range=hist_range,
    )
    divisions_mid = [
        (divisions[i] + divisions[i + 1]) / 2 for i, _ in enumerate(divisions[:-1])
    ]
    barrier_points = []
    barrier_stds = []
    for i in range(len(divisions) - 1):
        div_start = divisions[i]
        div_end = divisions[i + 1]
        sample = df[df[field] > div_start]
        sample = sample[sample[field] < div_end]
        stat = sample["empcorbarrier__barrier"].mean()  #!!! OR MEDIAN...?
        std = sample["empcorbarrier__barrier"].std()
        barrier_points.append(stat)
        barrier_stds.append(std)

    ax.errorbar(
        x=divisions_mid,
        y=barrier_points,
        yerr=barrier_stds,
        fmt="--o",
        # capsize=6,
        color="black",
    )

    # ----------

    return


# --------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

# start with a overall Figure canvas
fig = plt.figure(figsize=(12, 16))  # main--> (12, 12); SI-->(12, 16)

# Add a gridspec (which sets up a total of 3 subplots for us -- stacked on one another)
gs = fig.add_gridspec(
    # grid dimensions and column/row relative sizes
    nrows=6,  # main--> 3; SI-->7/7
    ncols=2,
    # width_ratios=(1, 1, 1),
    # height_ratios=(1, 1, 1),
    #
    # size of the overall grid (all axes together)
    left=0.1,
    right=0.9,
    bottom=0.1,
    top=0.9,
    #
    # spacing between subplots (axes)
    wspace=0.0,
    hspace=0.0,
)

# --------------------------------------------------------------------------------------

# LENGTH ALL
ax1 = fig.add_subplot(
    gs[0, 0],
    xlabel=r"Pathway Length ($\AA$)",
    ylabel="$E_{approx}$ [corrected] (eV)",
    xlim=(2.25, 5.1),
    ylim=(-0.5, 10),
)
add_scatter_and_trendline(ax1, df, "length", hist_bins=15, hist_range=(2.25, 5))
ax1.set_yticks([0,2.5,5,7.5,10])
# ax1.set_yticks([0, 25, 50])
# ax1.set_yticklabels(["0", "", "50"])
# ax1.set_xticks([-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0,])
# ax1.set_xticklabels(["-1.0", "", "-0.5", "", "0.0", "", "0.5", "", "1.0",])

# --------------------------------------------------------------------------------------

# EWALD ALL
ax2 = fig.add_subplot(
    gs[0, 1],
    xlabel=r"$\Delta$$E_{Ewald}$ (eV)",
    ylabel="$E_{approx}$ [corrected] (eV)",
    xlim=(-9, 21),
    ylim=(-0.25, 10),
)
add_scatter_and_trendline(
    ax2,
    df,
    "empiricalmeasuresb__ewald_energyb",
    hist_bins=15,
    hist_range=(-10, 20),
)
ax2.set_yticks([0,2.5,5,7.5,10])
# ax1.set_yticks([0, 25, 50])
# ax1.set_yticklabels(["0", "", "50"])
# ax1.set_xticks([-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0,])
# ax1.set_xticklabels(["-1.0", "", "-0.5", "", "0.0", "", "0.5", "", "1.0",])

# --------------------------------------------------------------------------------------

# Selecting subplots
"""
from most_common_structure_types.py

["alpha Rhenium trioxide", "ReO3", 13, 35],
# ['Orthorhombic Perovskite', 'CaTiO3', 21, 45],
# ['Cryolite', 'Na3AlF6', 130, 37],
# ['(Cubic) Perovskite', 'CaTiO3', 82, 152],  # meh
# ['F6GeK2', 'K2GeF6', 33, 26],
["AgLaOS", "LaAgSO", 27, 50],
# ['Scheelite', 'CaWO4', 15, 31],
["F4K2Ni", "K2NiF4", 23, 54],
["F3Fe", "FeF3", 15, 56],  # kinda extreme
# ['Double perovskite', 'Ba2MnWO6', 618, 220],
["alpha bismuth trifluoride", "BiF3", 27, 80],  # kinda like initial trend
# ['Li2MoF6', 'Li2MoF6', 22, 31],  # meh
# ['Matlockite', 'PbClF', 30, 49]]  # meh
"""

df_22 = df[df["structure__prototype3__number"] == 22]
df_53 = df[df["structure__prototype3__number"] == 53]
df_1457 = df[df["structure__prototype3__number"] == 1457]
df_1336 = df[df["structure__prototype3__number"] == 1336]

df_mlk = df[df["structure__prototype2__name"] == "Matlockite"]
df_art = df[df["structure__prototype2__name"] == "alpha Rhenium trioxide"]
df_opr = df[df["structure__prototype2__name"] == "Orthorhombic Perovskite"]
df_cry = df[df["structure__prototype2__name"] == "Cryolite"]
df_fgk = df[df["structure__prototype2__name"] == "F6GeK2"]
df_alo = df[df["structure__prototype2__name"] == "AgLaOS"]
df_scl = df[df["structure__prototype2__name"] == "Scheelite"]
df_fkn = df[df["structure__prototype2__name"] == "F4K2Ni"]
df_dpr = df[df["structure__prototype2__name"] == "Double perovskite"]
df_lmf = df[df["structure__prototype2__name"] == "Li2MoF6"]
# structure__prototype2__name
# structure__prototype2__formula_reduced

# dfs = [df_1457, df_mlk]
# colors = ["blue", "red"]
# change number of subplots above if you change the length of this


dfs = [
    # df_22,
    # df_53,
    # df_art,
    # df_opr,
    # df_1336,
    # df_cry,
    df_fgk,
    df_alo,
    df_scl,
    df_fkn,
    df_dpr,
    df_lmf,
]
colors = ["green"] * len(dfs)

# --------------------------------------------------------------------------------------

for i, (df_mini, color) in enumerate(zip(dfs, colors)):
    ax_new = fig.add_subplot(
        gs[i, 0],
        sharex=ax1,
        sharey=ax1,
        xlabel=r"Pathway Length ($\AA$)",
    )
    add_scatter_and_trendline(
        ax_new,
        df_mini,
        "length",
        color=color,
        hist_bins=15,
        hist_range=(2.25, 5),
    )

# --------------------------------------------------------------------------------------

for i, (df_mini, color) in enumerate(zip(dfs, colors)):
    ax_new = fig.add_subplot(
        gs[i, 1],
        sharex=ax2,
        sharey=ax2,
        xlabel=r"$\Delta$$E_{Ewald}$ (eV)",
    )
    add_scatter_and_trendline(
        ax_new,
        df_mini,
        "empiricalmeasuresb__ewald_energyb",
        color=color,
        hist_bins=15,
        hist_range=(-10, 20),
    )

# --------------------------------------------------------------------------------------

plt.savefig("ewald_and_length_split_SI.svg", format="svg")
