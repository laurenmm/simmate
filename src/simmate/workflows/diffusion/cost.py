# -*- coding: utf-8 -*-

import os

from pymatgen import MPRester
from pymatgen.core.composition import Composition
from pymatgen.analysis.cost import CostDBElements, CostAnalyzer, CostDBCSV

from prefect import Flow, Parameter, task
from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import (
    MaterialsProjectStructure as MPStructure,
    MatProjData2,
)


@task
def grab_data(structure_id):
    structure_db = MPStructure.objects.get(id=structure_id)
    structure = structure_db.to_pymatgen()

    # Grabbing cost
    comp = structure.composition
    # costs_orig = CostDBElements() ## Fluoride cost is super misleading
    try:
        costs_new = CostDBCSV(os.path.join(os.getcwd(), "element_prices.csv"))
        a = CostAnalyzer(costs_new)
        cost_kg = a.get_cost_per_kg(comp)
        cost_mol = a.get_cost_per_mol(comp)
    except:
        cost_kg = None
        cost_mol = None

    # Grabbing bandgap
    try:
        mpr = MPRester("2Tg7uUvaTAPHJQXl")
        data = mpr.query({"task_id": structure_id}, ["band_gap"])
        band_gap = data[0]["band_gap"]
    except:
        band_gap = None

    return cost_kg, cost_mol, band_gap


@task
def save_to_db(structure_id, new_data):

    cost_kg, cost_mol, band_gap = new_data

    p = MatProjData2(
        structure_id=structure_id,
        band_gap=band_gap,
        cost_per_mol=cost_mol,
        cost_per_kg=cost_kg,
    )
    p.save()

with Flow("PrototypeMatcher") as workflow:
    structure_id = Parameter("structure_id")
    data = grab_data(structure_id)
    save_to_db(structure_id, data)



from dask.distributed import Client

client = Client(preload="simmate.configuration.dask.init_django_worker")
structure_ids = (
    MPStructure.objects.filter(matprojdata2__isnull=True)
    .values_list("id", flat=True)
    .all()
)

client.map(
    workflow.run,
    [{"structure_id": id} for id in structure_ids],
    pure=False,
)
