# -*- coding: utf-8 -*-

from simmate.shortcuts import setup
from simmate.database.diffusion import Pathway as Pathway_DB
from django_pandas.io import read_frame

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
        structure__id="mp-27315",
        # structure__chemical_system="F-Mg-Ti", # Bi-F-O
        # structure__formula_reduced="LaF3", # BiOF
        # vaspcalca__energy_barrier__isnull=False,
        # structure__nelement__lte=4,
        # structure__chemical_system__contains="Pb",
        # structure__e_above_hull=0,
    )
    .order_by("structure__id", "vaspcalca__energy_barrier")
    # BUG: distinct() doesn't work for sqlite, only postgres. also you must have
    # "structure__id" as the first flag in order_by for this to work.
    .select_related("vaspcalca", "empiricalmeasures", "structure")
    # .distinct("structure__id")
    .all()
)

# ELECTROLYTES
# queryset = (
#     Pathway_DB.objects.filter(
#         structure__e_above_hull=0,
#         structure__matprojdata__band_gap__gte=3.5,
#         vaspcalca__energy_barrier__lte=1,
#         vaspcalca__energy_barrier__gte=0,
#         # vaspcalcb__isnull=True,
#         structure__matprojdata__cost_per_kg__lte=125,
#         structure__matprojdata__cost_per_mol__lte=125,
#         empiricalmeasures__dimensionality_cumlengths=3,
#     )
#     .order_by("structure__formula_reduced", "vaspcalca__energy_barrier")
#     # BUG: distinct() doesn't work for sqlite, only postgres. also you must have
#     # "structure__id" as the first flag in order_by for this to work.
#     .select_related("vaspcalca", "empiricalmeasures", "structure")
#     .distinct("structure__formula_reduced")
#     .all()
# )

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
#     .select_related("vaspcalca", "empiricalmeasures", "structure")
#     .distinct("structure__formula_reduced")
#     .all()
# )

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
        "vaspcalcb__energy_barrier",
        "empiricalmeasures__dimensionality",
        "empiricalmeasures__dimensionality_cumlengths",
    ],
)

# grabs barriers and makes a bar chart
# df = df.sort_values("vaspcalca__energy_barrier")
# ax = df.plot.barh(
#     "structure__formula_reduced",
#     "vaspcalca__energy_barrier",
#     width=0.85,
#     color="Green",
# )
# ax.get_legend().remove()
# ax.set_xlim(0, 1.5)
# ax.set_xlabel("Energy Barrier (eV)")
# ax.set_ylabel("")
# # ax.set_yticks([])
# fig = ax.get_figure()
# fig.set_size_inches(1, 3)
# fig.savefig("barh.svg", format="svg")

# df.to_csv("prototypes-1050_less-than-1eV-approx-barrier_one-path-per-structure.csv")


# Find which groups have at least 4 structures with <1eV pathways
# from tqdm import tqdm
# final_groups = []
# for group_num in tqdm(range(4936)):  # 4936
#     count = (
#         Pathway_DB.objects.filter(
#             vaspcalca__energy_barrier__gte=-1,
#             vaspcalca__energy_barrier__lte=1,
#             structure__prototype3__number=group_num,
#         )
#         .order_by(
#             "structure__id",
#             "vaspcalca__energy_barrier",
#         )
#         .select_related("vaspcalca", "empiricalmeasures", "structure")
#         .distinct("structure__id")
#         .count()
#     )
#     if count >= 4:
#         final_groups.append((group_num, count))

# from simmate.workflows.diffusion.vaspcalc_b import workflow
# result = workflow.run(pathway_id=3216, vasp_cmd="mpirun -n 28 vasp")

# from simmate.database.diffusion import VaspCalcB
# calc = VaspCalcB.objects.get(pathway_id=3216)
