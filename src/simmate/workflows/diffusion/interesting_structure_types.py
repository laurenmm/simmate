# -*- coding: utf-8 -*-

from simmate.shortcuts import setup
from simmate.database.diffusion import Pathway as Pathway_DB
from django_pandas.io import read_frame


queryset = (
    Pathway_DB.objects.filter(
        structure__prototype__formula_reduced__isnull=False,
        vaspcalca__energy_barrier__gte=-1,
        vaspcalca__energy_barrier__lte=1,
    )
    .order_by("structure__id", "vaspcalca__energy_barrier")
    .select_related("vaspcalca", "empiricalmeasures", "structure")
    .distinct("structure__id")
    .all()
)

queryset = (
    Pathway_DB.objects.filter(
        structure__chemical_system="F-La",
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
        "structure__formula_full",
        "structure__id",
        "structure__e_above_hull",
        "structure__prototype__name",
        "structure__prototype__formula_reduced",
        "vaspcalca__energy_barrier",
        "vaspcalcb__energy_barrier",
        "empiricalmeasures__dimensionality",
        "empiricalmeasures__dimensionality_cumlengths",
    ],
)


from simmate.shortcuts import setup
from simmate.database.diffusion import MaterialsProjectStructure
from django_pandas.io import read_frame

structures = MaterialsProjectStructure.objects.filter(
    prototype__formula_reduced__isnull=False
).all()

df = read_frame(
    structures,
    fieldnames=[
        "id",
        "formula_full",
        "id",
        "e_above_hull",
        "prototype__name",
        "prototype__formula_reduced",
    ],
)

