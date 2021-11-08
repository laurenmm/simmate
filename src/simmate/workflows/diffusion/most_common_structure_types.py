# -*- coding: utf-8 -*-

from tqdm import tqdm

from simmate.shortcuts import setup

from simmate.database.diffusion import Prototype3, Pathway, Prototype2

unique_numbers = Prototype3.objects.values_list("number", flat=True).distinct()

s_counts = []
p_counts = []
for n in tqdm(unique_numbers):
    cs = Prototype3.objects.filter(number=n).count()
    s_counts.append(cs)

    cp = Pathway.objects.filter(
        vaspcalca__energy_barrier__isnull=False,
        # structure__prototype2__formula_reduced="PbClF",
        structure__prototype3__number=n,
    ).count()
    p_counts.append(cp)


import pandas

df = pandas.DataFrame(
    {
        "group_id": unique_numbers,
        "s_count": s_counts,
        "p_count": p_counts,
    }
)

df_mini = df[(df.s_count > 10) & (df.p_count > 25)]

"""
# ID, scount, pcount
[[1457, 37, 36], 
 [53, 39, 77], 
  # [1336, 55, 84], --> bad
 [22, 131, 125]]


# [[1161,   14,   26],
# [  78,   11,   28],
[1457,   37,   36],
[  53,   39,   77],
# [  42,   15,   42], # meh
# [1336,   55,   84],
# [1389,   13,   27],
[  22,  131,  125],
# [1632,   20,   57], # meh
# [1099,   16,   30]]
"""

# --------------------------------------------------------------------------------------


from tqdm import tqdm

from simmate.shortcuts import setup

from simmate.database.diffusion import Prototype2, Pathway

unique_names = Prototype2.objects.values_list("formula_reduced", "name").distinct()

s_counts = []
p_counts = []
for formula, name in tqdm(unique_names):
    cs = Prototype2.objects.filter(formula_reduced=formula, name=name).count()
    s_counts.append(cs)

    cp = Pathway.objects.filter(
        vaspcalca__energy_barrier__isnull=False,
        # structure__prototype2__formula_reduced="PbClF",
        structure__prototype2__formula_reduced=formula,
        structure__prototype2__name=name,
    ).count()
    p_counts.append(cp)


import pandas

df = pandas.DataFrame(
    {
        "name": [n[1] for n in unique_names],
        "formula": [n[0] for n in unique_names],
        "s_count": s_counts,
        "p_count": p_counts,
    }
)

df_mini = df[(df.s_count > 10) & (df.p_count > 25)]


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
