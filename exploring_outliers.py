#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from simmate.shortcuts import setup
from simmate.database.diffusion import Pathway as Pathway_DB
from django_pandas.io import read_frame
from simmate.workflows.diffusion.utilities import get_oxi_supercell_path

"""


mp-559695 (3637)
ABC2D6 (225)


##
mp-8962 (1573)
AB2C4 (139)
#
mp-560449 (9852)
A2B3C7 (139)
#
mp-1147568 (9236)
A2B3C3D4 (139)
# This one is kinda similar
mp-21445 (9788)
A2B2C3D5 (139)
##

mp-753398 (18319)
W4O4F12

Be-F system (3376)
covalent contributions
change in covalency

"""


# --------------------------------------------------------------------------------------

# PATHWAYS TO FILTER BY

queryset = (
    Pathway_DB.objects.filter(
        length__lte=3,  # 3.5
        # structure__formula_anonymous="ABC2D6",
        # structure__spacegroup=225,
        structure__e_above_hull__lte=0.05,
        vaspcalca__energy_barrier__isnull=False,
        # vaspcalca__energy_barrier__gte=0,
        vaspcalca__energy_barrier__gte=1.75,
        empiricalmeasures__ionic_radii_overlap_anions__gt=-900,
        empiricalmeasures__ewald_energy__lte=0.15,  # 0.25
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
        "vaspcalcb__energy_barrier",
    ],
)
df.to_csv("pathways.csv")

# --------------------------------------------------------------------------------------

# INTERACTIVE PLOT

import plotly.express as px

fig = px.scatter(
    data_frame=df,
    x="length",
    y="empiricalmeasures__ewald_energy",
    color="vaspcalca__energy_barrier",
    range_color=[1.75, 2.25],
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
        "vaspcalcb__energy_barrier",
    ],
)
fig.show(renderer="browser", config={'scrollZoom': True})
fig.write_html("length_vs_ewald.html")

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

# VISUALIZE ALL PATHWAYS IN QUERY SET

for pathway in queryset:
    pathway_id = pathway.id
    path = Pathway_DB.objects.get(id=pathway_id)
    get_oxi_supercell_path(path.to_pymatgen(), 7).write_path(
        f"{pathway_id}.cif",
        nimages=5,
        # idpp=True,
    )
