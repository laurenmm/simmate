# -*- coding: utf-8 -*-

from simmate.workflows.diffusion.prototype_matcher_fork import AflowPrototypeMatcher
# from pymatgen.analysis.prototypes import AflowPrototypeMatcher


from prefect import Flow, Parameter, task
from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import (
    MaterialsProjectStructure as MPStructure,
    Prototype2 as Prototype, # !!! 
)


@task
def load_structure_from_db(structure_id):
    structure_db = MPStructure.objects.get(id=structure_id)
    structure = structure_db.to_pymatgen()
    return structure


@task
def find_prototype(structure):

    matcher = AflowPrototypeMatcher()
    prototype = matcher.get_prototypes(structure)
    prototype_name = prototype[0]["tags"]["mineral"] if prototype else None
    prototype_formula_reduced = (
        prototype[0]["snl"].structure.composition.reduced_formula if prototype else None
    )

    return (prototype_name, prototype_formula_reduced)


@task
def save_to_db(structure_id, prototype_data):

    prototype_name, prototype_formula_reduced = prototype_data

    p = Prototype(
        structure_id=structure_id,
        name=prototype_name,
        formula_reduced=prototype_formula_reduced,
    )
    p.save()


with Flow("PrototypeMatcher") as workflow:
    structure_id = Parameter("structure_id")
    structure = load_structure_from_db(structure_id)
    p_data = find_prototype(structure)
    save_to_db(structure_id, p_data)


# ----------------------------------------------------------------------------

# from tqdm import tqdm
# from dask.distributed import Client


# client = Client(preload="simmate.configuration.dask.init_django_worker")
# structure_ids = (
#     MPStructure.objects.filter(prototype2__isnull=True)
#     .values_list("id", flat=True)
#     .all()
# )

# client.map(
#     workflow.run,
#     [{"structure_id": id} for id in structure_ids],
#     pure=False,
# )
