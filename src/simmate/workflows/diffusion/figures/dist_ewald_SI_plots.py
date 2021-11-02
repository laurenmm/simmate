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
    )
    .select_related(
        "vaspcalca", "empiricalmeasures", "empiricalmeasuresb", "empcorbarrier"
    )
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
    ],
)

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

# add hist trend line
_, divisions = numpy.histogram(df["length"], bins=15)  # range=(0, 1)
divisions_mid = [
    (divisions[i] + divisions[i + 1]) / 2 for i, _ in enumerate(divisions[:-1])
]
barrier_stats = []
barrier_stds = []
for i in range(len(divisions) - 1):
    div_start = divisions[i]
    div_end = divisions[i + 1]
    sample = df[df["length"] > div_start]
    sample = sample[sample["length"] < div_end]
    stat = sample["empcorbarrier__barrier"].mean()  #!!! OR MEDIAN...?
    std = sample["empcorbarrier__barrier"].std()
    barrier_stats.append(stat)
    barrier_stds.append(std)
ax.errorbar(
    x=divisions_mid,
    y=barrier_stats,
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

# add hist trend line
_, divisions = numpy.histogram(
    df["empiricalmeasuresb__ewald_energyb"], bins=15, range=(-10, 20)
)
divisions_mid = [
    (divisions[i] + divisions[i + 1]) / 2 for i, _ in enumerate(divisions[:-1])
]
barrier_stats = []
barrier_stds = []
for i in range(len(divisions) - 1):
    div_start = divisions[i]
    div_end = divisions[i + 1]
    sample = df[df["empiricalmeasuresb__ewald_energyb"] > div_start]
    sample = sample[sample["empiricalmeasuresb__ewald_energyb"] < div_end]
    stat = sample["empcorbarrier__barrier"].mean()  #!!! OR MEDIAN...?
    std = sample["empcorbarrier__barrier"].std()
    barrier_stats.append(stat)
    barrier_stds.append(std)
ax.errorbar(
    x=divisions_mid,
    y=barrier_stats,
    yerr=barrier_stds,
    fmt="--o",
    # capsize=6,
    color="black",
)


# plt.show()
plt.savefig("ewald_only.svg", format="svg")

# --------------------------------------------------------------------------------------
