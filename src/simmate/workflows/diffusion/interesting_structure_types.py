# -*- coding: utf-8 -*-

from simmate.shortcuts import setup
from simmate.database.diffusion import Pathway as Pathway_DB
from django_pandas.io import read_frame

# FeClO
# PbClF
# 17
# 42
# 48
# 1027
# queryset = (
#     Pathway_DB.objects.filter(
#         # structure__prototype2__formula_reduced__isnull=False,
#         # structure__prototype2__formula_reduced="PbClF",
#         vaspcalca__energy_barrier__gte=0,
#         vaspcalca__energy_barrier__lte=1.5,
#         structure__prototype3__number=1027,
#     )
#     .order_by(
#         "structure__id",
#         "vaspcalca__energy_barrier",
#     )
#     .select_related("vaspcalca", "empiricalmeasures", "structure")
#     .distinct("structure__id")
#     .all()
# )

queryset = (
    Pathway_DB.objects.filter(
        # structure__chemical_system="F-Pb", # Bi-F-O
        # structure__formula_reduced="LaF3", # BiOF
        vaspcalca__energy_barrier__isnull=False,
        structure__nelement__lte=4,
        structure__chemical_system__contains="Pb",
    )
    .order_by("structure__id", "vaspcalca__energy_barrier")
    # BUG: distinct() doesn't work for sqlite, only postgres. also you must have
    # "structure__id" as the first flag in order_by for this to work.
    .select_related("vaspcalca", "empiricalmeasures", "structure")
    .distinct("structure__id")
    .all()
)

df = read_frame(
    queryset,
    fieldnames=[
        "id",
        # "length",
        "structure__nelement",
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
