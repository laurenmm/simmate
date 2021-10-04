#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 10:23:51 2021

@author: jacksund
"""

from simmate.shortcuts import setup
from simmate.database.diffusion import MaterialsProjectStructure
from django_pandas.io import read_frame

queryset = MaterialsProjectStructure.objects.filter(
    prototype2__formula_reduced__isnull=True
).all()

df = read_frame(
    queryset,
    fieldnames=[
        "id",
        "formula_full",
        "id",
        "e_above_hull",
        "prototype__name",
        "prototype__formula_reduced",
    ],
)

structures = [s.to_pymatgen() for s in queryset]

from pymatgen.analysis.structure_matcher import StructureMatcher
from simmate.database.diffusion import Prototype3

matcher = StructureMatcher(attempt_supercell=False)
# result = matcher.group_structures(structures, anonymous=True)

from tqdm import tqdm

matching_groups = []
group_ids = []
for structure, db_entry in tqdm(zip(structures, queryset)):
    found_match = False
    for index, group in enumerate(matching_groups):
        first_structure = group[0]
        if matcher.fit_anonymous(structure, first_structure):
            found_match = True
            group.append(structure)
            group_ids.append(index)

            p = Prototype3(structure=db_entry, number=index)
            p.save()

            break

    if not found_match:
        next_index = len(matching_groups)
        group_ids.append(next_index)
        matching_groups.append([structure])
        p = Prototype3(structure=db_entry, number=next_index)
        p.save()
