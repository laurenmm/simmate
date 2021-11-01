# -*- coding: utf-8 -*-

# import copy
from datetime import timedelta

from prefect import Flow, Parameter, task

from prefect.triggers import all_finished

from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import (
    Pathway as Pathway_DB,
    EmpiricalMeasuresD as EM_DB,
)
from simmate.workflows.diffusion.utilities import get_oxi_supercell_path

# --------------------------------------------------------------------------------------


@task
def load_pathway_from_db(pathway_id):

    # grab the pathway model object
    pathway_db = Pathway_DB.objects.get(id=pathway_id)

    # convert the pathway to pymatgen MigrationPath
    path = pathway_db.to_pymatgen()

    return path


# --------------------------------------------------------------------------------------


@task
def get_ionic_radii_overlap(path):

    # Let's run this within a supercell structure
    supercell_path = get_oxi_supercell_path(path, min_sl_v=7, oxi=True)

    # let's grab all of the pathway images
    images = supercell_path.get_structures(
        nimages=5,
        # vac_mode=True,  # vacancy mode
        idpp=True,
        # **idpp_kwargs,
        # species = 'Li', # Default is None. Set this if I only want one to move
    )
    # NOTE: the diffusion atom is always the first site in these structures (index=0)

    # Finding max change in anion, cation, and nuetral atom overlap
    overlap_data = []

    for image in images:

        # grab the diffusing ion. This is always index 0. Also grab it's radius
        moving_site = image[0]
        moiving_site_radius = moving_site.specie.ionic_radius

        # grab the diffusing ion's nearest neighbors within 8 angstroms and include
        # neighboring unitcells
        moving_site_neighbors = image.get_neighbors(
            moving_site,
            r=8.0,
            include_image=True,
        )

        # This is effective our empty starting list. I set these to -999 to ensure
        # they are changed.
        max_overlap = -999
        for neighbor, distance, _, _ in moving_site_neighbors:
            neighbor_radius = neighbor.specie.ionic_radius
            overlap = moiving_site_radius + neighbor_radius - distance
            if overlap > max_overlap:
                max_overlap = overlap
        overlap_data.append(max_overlap)
    # make lists into relative values
    overlap_data_rel = [(image - overlap_data[0]) for image in overlap_data]

    # grab the maximum deviation from 0. Note this can be negative!
    ionic_radii_overlap = max(overlap_data_rel, key=abs)

    return ionic_radii_overlap


# --------------------------------------------------------------------------------------

# NOTE: if an entry already exists for this pathway, it is overwritten


@task(trigger=all_finished, max_retries=3, retry_delay=timedelta(seconds=5))
def add_empiricalmeasures_to_db(pathway_id, iro):
    em_data = EM_DB(
        status="C",
        pathway_id=pathway_id,
        ionic_radii_overlap=iro if not isinstance(iro, Exception) else None,
    )
    em_data.save()


# --------------------------------------------------------------------------------------


# now make the overall workflow
with Flow("Empirical Measures for Pathway") as workflow:

    # load the structure object from our database
    pathway_id = Parameter("pathway_id")

    # load the pathway object from our database
    pathway = load_pathway_from_db(pathway_id)

    # calculate all of the empirical data
    iro = get_ionic_radii_overlap(pathway)

    # save the data to our database
    add_empiricalmeasures_to_db(pathway_id, iro)

# for Prefect Cloud compatibility, set the storage to an import path
# workflow.storage = LocalStorage(path=f"{__name__}:workflow", stored_as_script=True)

# --------------------------------------------------------------------------------------

from dask.distributed import Client

client = Client(preload="simmate.configuration.dask.init_django_worker")
pathway_ids = (
    Pathway_DB.objects.filter(empiricalmeasuresd__isnull=True)
    .values_list("id", flat=True)
    .all()
)

client.map(
    workflow.run,
    [{"pathway_id": id} for id in pathway_ids],
    pure=False,
)
