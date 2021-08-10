# -*- coding: utf-8 -*-

import numpy

# import copy
from datetime import timedelta

from prefect import Flow, Parameter, task

from prefect.triggers import all_finished

# from prefect.storage import Local as LocalStorage

# from pymatgen_diffusion.neb.full_path_mapper import FullPathMapper

from pymatgen.analysis.ewald import EwaldSummation

# from pymatgen.analysis.local_env import ValenceIonicRadiusEvaluator

from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import (
    Pathway as Pathway_DB,
    EmpiricalMeasuresB as EM_DB,
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
def get_ewald_energy(path):

    # Let's run this within a supercell structure
    supercell_path = get_oxi_supercell_path(path, min_sl_v=7, oxi=True)

    images = supercell_path.get_structures(
        nimages=1,
        # vac_mode=True,  # vacancy mode
        idpp=True,
        # **idpp_kwargs,
        # species = 'Li', # Default is None. Set this if I only want one to move
    )
    # NOTE: the diffusion atom is always the first site in these structures (index=0)

    # print(images[0])

    ewald_energies = []
    ewald_forces = []
    for image in images:
        ewald_calculator = EwaldSummation(image, compute_forces=True)  # accuracy=3
        ewald_energy = ewald_calculator.total_energy
        ewald_force = numpy.linalg.norm(ewald_calculator.forces)
        # NOTE: requires oxidation state decorated structure
        ewald_energies.append(ewald_energy)
        ewald_forces.append(ewald_force)

    # These are a series of different measures that I'm testing
    a = ewald_energies[1] - ewald_energies[0]
    b = (ewald_energies[1] - ewald_energies[0]) / abs(ewald_energies[0])
    c = ewald_energies[0]
    d = ewald_energies[1]
    e = ewald_forces[1] - ewald_forces[0]
    f = (ewald_forces[1] - ewald_forces[0]) / abs(ewald_forces[0])

    return a, b, c, d, e, f


# --------------------------------------------------------------------------------------

# NOTE: if an entry already exists for this pathway, it is overwritten


@task(trigger=all_finished, max_retries=3, retry_delay=timedelta(seconds=5))
def add_empiricalmeasures_to_db(pathway_id, ewald_data):

    # unpack data from all my different versions above.
    a, b, c, d, e, f = ewald_data

    # now add the empirical data using the supplied dictionary
    # NOTE: the "if not __ else None" code is to make sure there wasn't an error
    # raise in one of the upstream tasks. For example there was an error, oxi_data
    # would be an excpetion class -- in that case, we choose to store None instead
    # of the exception itself.
    em_data = EM_DB(
        status="C",
        pathway_id=pathway_id,
        #
        # ewald_energy=ewald_data if not isinstance(ewald_data, Exception) else None,
        ewald_energya=a if not isinstance(a, Exception) else None,
        ewald_energyb=b if not isinstance(b, Exception) else None,
        ewald_energyc=c if not isinstance(c, Exception) else None,
        ewald_energyd=d if not isinstance(d, Exception) else None,
        ewald_energye=e if not isinstance(e, Exception) else None,
        ewald_energyf=f if not isinstance(f, Exception) else None,
        #
        # ionic_radii_overlap_cations=iro_data[0]
        # if not isinstance(iro_data, Exception)
        # else None,
        # #
        # ionic_radii_overlap_anions=iro_data[1]
        # if not isinstance(iro_data, Exception)
        # else None,
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
    ewald_data = get_ewald_energy(pathway)

    # save the data to our database
    add_empiricalmeasures_to_db(pathway_id, ewald_data)

# for Prefect Cloud compatibility, set the storage to an import path
# workflow.storage = LocalStorage(path=f"{__name__}:workflow", stored_as_script=True)

# --------------------------------------------------------------------------------------
