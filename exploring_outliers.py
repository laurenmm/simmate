#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from simmate.shortcuts import setup
from simmate.database.diffusion import Pathway as Pathway_DB
from django_pandas.io import read_frame
from simmate.workflows.diffusion.utilities import get_oxi_supercell_path

# --------------------------------------------------------------------------------------

# PATHWAYS TO FILTER BY

queryset = (
    Pathway_DB.objects.filter(
        # structure__formula_anonymous="ABC2D6",
        # structure__spacegroup=225,
        vaspcalca__energy_barrier__isnull=False,
        vaspcalca__energy_barrier__gte=0,
        vaspcalca__energy_barrier__lte=1,
        empiricalmeasures__ionic_radii_overlap_anions__gt=-900,
    )
    .select_related("vaspcalca", "empiricalmeasures", "structure")
    .all()
)

# --------------------------------------------------------------------------------------

# TABLE TO MAKE WITH PATHWAYS

df = read_frame(
    queryset,
    fieldnames=[
        "id",
        "length",
        "structure__id",
        "structure__formula_full",
        "structure__spacegroup",
        "structure__formula_anonymous",
        "structure__e_above_hull",
        "empiricalmeasures__ewald_energy",
        "vaspcalca__energy_barrier",
    ],
)


# --------------------------------------------------------------------------------------

# INTERACTIVE PLOT

import plotly.express as px

fig = px.scatter(
    data_frame=df,
    x="length",
    y="empiricalmeasures__ewald_energy",
    color="vaspcalca__energy_barrier",
    range_color=[0, 1.1],
    hover_data=[
        "id",
        "length",
        "structure__id",
        "structure__formula_full",
        "structure__spacegroup",
        "structure__formula_anonymous",
        "structure__e_above_hull",
        "empiricalmeasures__ewald_energy",
        "vaspcalca__energy_barrier",
    ],
)
fig.show(renderer="browser", config={'scrollZoom': True})

# --------------------------------------------------------------------------------------

# SEARCH FOR PATHWAYS AND EXTRA DATA

queryset = (
    Pathway_DB.objects.filter(
        structure__id="mp-554144",
    ).order_by("vaspcalca__energy_barrier")
    .select_related("vaspcalca", "empiricalmeasures", "structure")
    .all()
)

df = read_frame(
    queryset,
    fieldnames=[
        "id",
        "length",
        "structure__formula_full",
        "structure__id",
        "structure__e_above_hull",
        "structure__spacegroup",
        "structure__formula_anonymous",
        "nsites_777",
        "nsites_101010",
        "vaspcalca__energy_barrier",
        "vaspcalcb__energy_barrier",
        "vaspcalcc__energy_barrier",
        "empiricalmeasures__dimensionality",
        "empiricalmeasures__dimensionality_cumlengths",
    ],
)


# --------------------------------------------------------------------------------------

# VISUALIZE PATHWAY

pathway_id = 24641
path = Pathway_DB.objects.get(id=pathway_id)
get_oxi_supercell_path(path.to_pymatgen(), 7).write_path(
    f"{pathway_id}.cif",
    nimages=5,
    # idpp=True,
)

# --------------------------------------------------------------------------------------

