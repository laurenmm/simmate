# -*- coding: utf-8 -*-

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
    ],
)

# --------------------------------------------------------------------------------------

# Grabbing substructure types to plot as well.

# group_ids = [53, 1457, 22]  # 22
# colors = ["red", "blue", "orange"]

group_ids = [
    53,
    1457,
    22,
    # 1336,
    # "purple",
    # "brown",
    # "pink",
    # "grey",
    # "olive",
    # "cyan",
]
colors = [
    "blue",
    "red",
    "green",
    # "orange",
    # "purple",
    # "brown",
    # "pink",
    # "grey",
    # "olive",
    # "cyan",
]


def get_trendline(df, field, hist_bins=None, hist_range=None):
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

    return divisions_mid, barrier_points, barrier_stds


# --------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

# start with a square Figure
fig = plt.figure(figsize=(4 * 1.618, 4))  # golden ratio = 1.618

# Add axes for the main plot
ax = fig.add_subplot(
    xlabel=r"Pathway Length ($\AA$)",
    ylabel="$E_{approx}$ [corrected] (eV)",
    xlim=(2.25, 5.1),
    ylim=(-0.5, 10),
)

# add the data as a scatter
hb = ax.scatter(
    x=df["length"],  # X
    y=df["empcorbarrier__barrier"],  # Y
    c="green",
    alpha=0.25,
)

# # plot trendlines for subgroups too
# for group, color in zip(group_ids, colors):
#     df_mini = df[df["structure__prototype3__number"] == group]
#     # hb = ax.scatter(
#     #     x=df_mini["length"],  # X
#     #     y=df_mini["empcorbarrier__barrier"],  # Y
#     #     c=color,
#     #     alpha=0.25,
#     # )
#     divisions_mid, barrier_points, barrier_stds = get_trendline(
#         df_mini,
#         field="length",
#         hist_bins=15,
#         hist_range=(2.25, 5),
#     )
#     ax.errorbar(
#         x=divisions_mid,
#         y=barrier_points,
#         yerr=barrier_stds,
#         fmt="--o",
#         # capsize=6,
#         color=color,
#         # alpha=0.75,
#     )

# add hist trend line
divisions_mid, barrier_points, barrier_stds = get_trendline(
    df, field="length", hist_bins=15, hist_range=(2.25, 5)
)
ax.errorbar(
    x=divisions_mid,
    y=barrier_points,
    yerr=barrier_stds,
    fmt="--o",
    # capsize=6,
    color="black",
)

# plt.show()
plt.savefig("length_only.svg", format="svg")

# --------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

# start with a square Figure
fig = plt.figure(figsize=(4 * 1.618, 4))  # golden ratio = 1.618

# Add axes for the main plot
ax = fig.add_subplot(
    xlabel=r"$\Delta$ $E_{Ewald}$ (eV)",
    ylabel="$E_{approx}$ [corrected] (eV)",
    xlim=(-9, 21),
    ylim=(-0.25, 10),
)

# add the data as a scatter
hb = ax.scatter(
    x=df["empiricalmeasuresb__ewald_energyb"],  # X
    y=df["empcorbarrier__barrier"],  # Y
    c="green",
    alpha=0.25,
)

# # plot trendlines for subgroups too
# for group, color in zip(group_ids, colors):
#     df_mini = df[df["structure__prototype3__number"] == group]
#     # hb = ax.scatter(
#     #     x=df_mini["empiricalmeasuresb__ewald_energyb"],  # X
#     #     y=df_mini["empcorbarrier__barrier"],  # Y
#     #     c=color,
#     #     alpha=0.25,
#     # )
#     divisions_mid, barrier_points, barrier_stds = get_trendline(
#         df_mini,
#         field="empiricalmeasuresb__ewald_energyb",
#         hist_bins=15,
#         hist_range=(-10, 20),
#     )
#     ax.errorbar(
#         x=divisions_mid,
#         y=barrier_points,
#         yerr=barrier_stds,
#         fmt="--o",
#         # capsize=6,
#         color=color,
#         # alpha=0.75,
#     )

# add hist trend line
divisions_mid, barrier_points, barrier_stds = get_trendline(
    df, field="empiricalmeasuresb__ewald_energyb", hist_bins=15, hist_range=(-10, 20)
)
ax.errorbar(
    x=divisions_mid,
    y=barrier_points,
    yerr=barrier_stds,
    fmt="--o",
    # capsize=6,
    color="black",
)

plt.show()
# plt.savefig("ewald_only.svg", format="svg")

# --------------------------------------------------------------------------------------
