# -*- coding: utf-8 -*-

from simmate.shortcuts import setup
from simmate.database.diffusion import Pathway as Pathway_DB
from django_pandas.io import read_frame

# ----------------------------------------------------------------------------

# STRUCTURE TYPES

# Find which groups have at least N structures with <1eV pathways
# from tqdm import tqdm
# final_groups = []
# for group_num in tqdm(range(4936)):  # 4936
#     count = (
#         Pathway_DB.objects.filter(
#             # vaspcalca__energy_barrier__gte=-1,
#             # vaspcalca__energy_barrier__lte=1,
#             # structure__e_above_hull=0,
#             empcorbarrier__barrier__gte=0,
#             empcorbarrier__barrier__lte=1,
#             structure__prototype3__number=group_num,
#             structure__hostlattice__dimension=2,
#             empiricalmeasures__dimensionality_cumlengths=2,
#         )
#         .order_by(
#             "structure__id",
#             # "vaspcalca__energy_barrier",
#             "empcorbarrier__barrier",
#         )
#         .distinct("structure__id")
#         .count()
#     )
#     if count >= 3:
#         final_groups.append((group_num, count))

# This query set let's me view all structure types linked to AFLOW
# queryset = (
#     Pathway_DB.objects.filter(
#         structure__prototype2__formula_reduced__isnull=False,
#         empcorbarrier__barrier__gte=-1,
#         empcorbarrier__barrier__lte=1,
#         structure__e_above_hull=0,
#         structure__hostlattice__dimension=2,
#         empiricalmeasures__dimensionality_cumlengths=2,
#     )
#     .order_by(
#         "structure__id",
#         "vaspcalca__energy_barrier",
#     )
#     .select_related("vaspcalca", "empiricalmeasures", "structure")
#     .distinct("structure__id")
#     .all()
# )

# (group_number, count)
# 2D host lattice, 2D cumlengths path
# (17, 3)
# (42, 10)
# (48, 6)
# (68, 1) -- not interc...?
# (117, 1) -- not interc
# (257, 2) -- not interc
# (388, 1)
# (1027, 4)
# (1097, 1) -- not interc
# (1336, 2) -- not interc
# (1799, 1)
# (1816, 1) -- not interc
# (2074, 1) -- not interc
# (2082, 2) -- not interc
# (2229, 2) -- not interc
# (2277, 2) -- not interc
# (2628, 1)
# (2727, 3) -- molecular SO2F (sulfonyl fluoride)
#
# Ca(Cu2P)2, 1 -- unstable host lattice
# Ce2SO2, 1
# K2NiF4 -- not interc
# LaAgSO, 11
# LiCaAlF6 -- not interc
# PbClF, 14
# Sr3Ti2O7 -- not interc
# SrUO4 -- not interc
# TiAl3 -- not interc
# Ca(Cu2P)2 -- not interc

# queryset = (
#     Pathway_DB.objects.filter(
#         # structure__prototype2__formula_reduced="PbClF",
#         structure__prototype3__number=17,
#         structure__e_above_hull=0,
#         empcorbarrier__barrier__gte=0,
#         empcorbarrier__barrier__lte=1,
#         structure__hostlattice__dimension=2,
#         empiricalmeasures__dimensionality_cumlengths=2,
#     )
#     .order_by(
#         "structure__id",
#         "vaspcalca__energy_barrier",
#     )
#     .select_related("vaspcalca", "empiricalmeasures", "structure")
#     .distinct("structure__id")
#     .all()
# )

# SEARCHING BY COMPOSITION OR ID
# mp-315
# mp-905
# mp-6949
# mp-588
# mvc-14678
# mp-1539332
# mp-3881
# mp-8291
# mp-34291
# mp-1208602
# mp-27315
queryset = (
    Pathway_DB.objects.filter(
        # structure__prototype2__formula_reduced="PbClF",
        structure__prototype3__number=1027,
        # structure__id="mp-1218175",
        # structure__chemical_system="F-Mg-Ti", # Bi-F-O
        # structure__formula_reduced="LaF3", # BiOF
        vaspcalca__energy_barrier__isnull=False,
        # structure__nelement__lte=4,
        # structure__chemical_system__contains="Pb",
        # structure__e_above_hull=0,
    )
    .order_by("structure__id", "vaspcalca__energy_barrier")
    # BUG: distinct() doesn't work for sqlite, only postgres. also you must have
    # "structure__id" as the first flag in order_by for this to work.
    .select_related("vaspcalca", "empiricalmeasures", "structure", "empcorbarrier")
    .distinct("structure__id")
    .all()
)

# ----------------------------------------------------------------------------

# ELECTROLYTES
# queryset = (
#     Pathway_DB.objects.filter(
#         structure__e_above_hull=0,
#         structure__matprojdata__band_gap__gte=3.5,
#         # vaspcalca__energy_barrier__lte=1,
#         # vaspcalca__energy_barrier__gte=0,
#         empcorbarrier__barrier__gte=0,
#         empcorbarrier__barrier__lte=0.7,
#         # vaspcalcb__isnull=True,
#         structure__matprojdata__cost_per_kg__lte=125,
#         structure__matprojdata__cost_per_mol__lte=125,
#         empiricalmeasures__dimensionality_cumlengths=3,
#     )
#     .order_by("structure__formula_reduced", "vaspcalca__energy_barrier")
#     # BUG: distinct() doesn't work for sqlite, only postgres. also you must have
#     # "structure__id" as the first flag in order_by for this to work.
#     .select_related("vaspcalca", "empiricalmeasures", "structure", "empcorbarrier")
#     .distinct("structure__formula_reduced")
#     .all()
# )

# ----------------------------------------------------------------------------

# ELECTRODES
# queryset = (
#     Pathway_DB.objects.filter(
#         structure__e_above_hull=0,
#         structure__matprojdata__band_gap__lte=0.5,
#         # vaspcalca__energy_barrier__lte=1,
#         vaspcalca__energy_barrier__gte=0,
#         # structure__matprojdata__cost_per_kg__lte=500,
#         # structure__matprojdata__cost_per_mol__lte=500,
#         empiricalmeasures__dimensionality_cumlengths=2,
#         # empiricalmeasures__dimensionality=2,
#     )
#     .order_by("structure__formula_reduced", "vaspcalca__energy_barrier")
#     # BUG: distinct() doesn't work for sqlite, only postgres. also you must have
#     # "structure__id" as the first flag in order_by for this to work.
#     .select_related("vaspcalca", "empiricalmeasures", "structure", "empcorbarrier")
#     .distinct("structure__formula_reduced")
#     .all()
# )

# ----------------------------------------------------------------------------

# FOR STRUCTURE-TYPE PLOT BELOW
# PbClF*, LaAgSO*, Ce2SO2
# [17*, 42*, 48*, 388, 1027*, 1799, 2628]
# queryset = (
#     Pathway_DB.objects.filter(
#         # structure__prototype2__formula_reduced="LaAgSO",
#         structure__prototype3__number=17,
#         # structure__e_above_hull=0,
#         empcorbarrier__barrier__gte=0,
#         empcorbarrier__barrier__lte=1,
#         structure__hostlattice__dimension=2,
#         empiricalmeasures__dimensionality_cumlengths=2,
#     )
#     .order_by(
#         "structure__id",
#         "vaspcalca__energy_barrier",
#     )
#     .select_related("vaspcalca", "empiricalmeasures", "structure")
#     .distinct("structure__id")
#     .all()
# )

# ----------------------------------------------------------------------------


df = read_frame(
    queryset,
    fieldnames=[
        "id",
        "nsites_777",
        "nsites_101010",
        # "length",
        "structure__nelement",
        "structure__matprojdata__band_gap",
        "structure__matprojdata__cost_per_kg",
        "structure__matprojdata__cost_per_mol",
        "structure__formula_full",
        "structure__formula_reduced",
        "structure__id",
        "structure__e_above_hull",
        "structure__prototype2__name",
        "structure__prototype2__formula_reduced",
        "structure__prototype3__number",
        "vaspcalca__energy_barrier",
        "empcorbarrier__barrier",
        "vaspcalcb__energy_barrier",
        "empiricalmeasures__dimensionality",
        "empiricalmeasures__dimensionality_cumlengths",
    ],
)

# ----------------------------------------------------------------------------


# # grabs barriers and makes a bar chart
# df = df.sort_values("empcorbarrier__barrier")
# df = df[:12]
# ax = df.plot.barh(
#     "structure__formula_reduced",
#     "empcorbarrier__barrier",
#     width=0.85,
#     color="Green",
# )
# ax.get_legend().remove()
# ax.set_xlim(0, 1)
# ax.set_xlabel("Energy Barrier (eV)")
# ax.set_ylabel("")
# ax.set_xticks([0,0.5,1])
# fig = ax.get_figure()
# fig.set_size_inches(1, 3)
# # fig.show()
# fig.savefig("barh.svg", format="svg")


# ----------------------------------------------------------------------------

# from simmate.workflows.diffusion.vaspcalc_b import workflow
# result = workflow.run(pathway_id=3216, vasp_cmd="mpirun -n 28 vasp")

# from simmate.database.diffusion import VaspCalcB
# calc = VaspCalcB.objects.get(pathway_id=3216)
