# -*- coding: utf-8 -*-

from pymatgen.analysis.local_env import CrystalNN
from pymatgen.analysis.dimensionality import get_dimensionality_larsen

from prefect import Flow, Parameter, task
from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import (
    MaterialsProjectStructure as MPStructure,
    HostLattice
)


@task
def load_structure_from_db(structure_id):
    structure_db = MPStructure.objects.get(id=structure_id)
    structure = structure_db.to_pymatgen()
    return structure


@task
def get_host_dimension(structure):
    
    structure.remove_species("F")
    
    bonded_structure = CrystalNN().get_bonded_structure(structure)

    dimensionality = get_dimensionality_larsen(bonded_structure)

    return dimensionality


@task
def save_to_db(structure_id, dim):

    p = HostLattice(
        structure_id=structure_id,
        dimension=dim,
    )
    p.save()


with Flow("PrototypeMatcher") as workflow:
    structure_id = Parameter("structure_id")
    structure = load_structure_from_db(structure_id)
    dim = get_host_dimension(structure)
    save_to_db(structure_id, dim)


# ----------------------------------------------------------------------------

from tqdm import tqdm
from dask.distributed import Client


client = Client(preload="simmate.configuration.dask.init_django_worker")
structure_ids = (
    MPStructure.objects.filter(hostlattice__isnull=True)
    .values_list("id", flat=True)
    .all()
)

client.map(
    workflow.run,
    [{"structure_id": id} for id in structure_ids],
    pure=False,
)
