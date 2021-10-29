# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------


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
fig = plt.figure(figsize=(5 * 1.618, 5))  # golden ratio = 1.618

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

plt.show()

# --------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

# start with a square Figure
fig = plt.figure(figsize=(5 * 1.618, 5))  # golden ratio = 1.618

# Add axes for the main plot
ax = fig.add_subplot(
    xlabel=r"$\Delta$ Ewald Energy (eV)",
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

plt.show()

# --------------------------------------------------------------------------------------
