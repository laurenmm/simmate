# -*- coding: utf-8 -*-

# import numpy
from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import Pathway as Pathway_DB, Relative

queryset = (
    Pathway_DB.objects.filter(
        relative__isnull=True,
        empcorbarrier__barrier__isnull=False,
    )
    .select_related("structure", "vaspcalca")
    .all()
)

from tqdm import tqdm

for pathway in tqdm(queryset):

    # make sure that at least 2 paths have barriers
    if (
        pathway.structure.pathways.filter(
            vaspcalca__energy_barrier__isnull=False
        ).count()
        < 2
    ):
        continue

    shortest_length = pathway.structure.pathways.order_by("length").first().length

    smallest_barrier = (
        pathway.structure.pathways.order_by("vaspcalca__energy_barrier")
        .first()
        .empcorbarrier.barrier
    )

    r = Relative(
        length=(pathway.length - shortest_length) / shortest_length,
        barrier=pathway.empcorbarrier.barrier - smallest_barrier,
        pathway=pathway,
    )
    r.save()
