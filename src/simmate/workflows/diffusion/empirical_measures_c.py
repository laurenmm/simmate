# -*- coding: utf-8 -*-

import numpy

# import copy
from datetime import timedelta

from prefect import Flow, Parameter, task

from prefect.triggers import all_finished

# from prefect.storage import Local as LocalStorage

# from pymatgen_diffusion.neb.full_path_mapper import FullPathMapper
from pymatgen.analysis.ewald import EwaldSummation

from pymatgen.analysis.local_env import CrystalNN
from pymatgen.analysis.local_env import ValenceIonicRadiusEvaluator
from matminer.featurizers.site import AverageBondLength

from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.chemenv.coordination_environments.chemenv_strategies import (
    SimplestChemenvStrategy,
)
from pymatgen.analysis.chemenv.coordination_environments.coordination_geometries import (
    AllCoordinationGeometries,
)
from pymatgen.analysis.chemenv.coordination_environments.coordination_geometry_finder import (
    LocalGeometryFinder,
)
from pymatgen.analysis.chemenv.coordination_environments.structure_environments import (
    LightStructureEnvironments,
)

from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import (
    Pathway as Pathway_DB,
    EmpiricalMeasuresC as EM_DB,
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
    supercell_path = get_oxi_supercell_path(path, min_sl_v=7, oxi=True, new_oxi=True)

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
    a = (ewald_energies[1] - ewald_energies[0]) / abs(ewald_energies[0])
    b = ewald_energies[1] - ewald_energies[0]
    c = (ewald_energies[1] - ewald_energies[0]) / image.num_sites
    d = (ewald_energies[1] - ewald_energies[0]) * ewald_energies[0]
    e = (ewald_energies[1] - ewald_energies[0]) * (ewald_energies[0] / image.num_sites)
    f = ewald_energies[0] / image.num_sites
    g = ewald_energies[1] / image.num_sites

    h = ewald_forces[1] - ewald_forces[0]
    i = (ewald_forces[1] - ewald_forces[0]) / abs(ewald_forces[0])
    j = (ewald_forces[1] - ewald_forces[0]) / image.num_sites

    return a, b, c, d, e, f, g, h, i, j


# --------------------------------------------------------------------------------------


@task
def get_average_bond_length(path):

    # run oxidation analysis on structure
    # structure = ValenceIonicRadiusEvaluator(path.symm_structure).structure
    # grab the oxidation state of the diffusing ion
    # specie = structure.equivalent_sites[path.iindex][0].specie
    # average_length_bulk = featurizer.featurize(structure, )  # cant grab the index easily...

    featurizer = AverageBondLength(CrystalNN())

    # Let's run this within a supercell structure
    supercell_path = get_oxi_supercell_path(path, min_sl_v=7, oxi=True, new_oxi=True)

    images = supercell_path.get_structures(
        nimages=1,
        # vac_mode=True,  # vacancy mode
        idpp=True,
        # **idpp_kwargs,
        # species = 'Li', # Default is None. Set this if I only want one to move
    )

    average_lengths = []
    for image in images:
        average_length = featurizer.featurize(image, 0)[0]  # index=0 for diffusing atom
        average_lengths.append(average_length)

    # test with different measures
    x = average_lengths[0]
    y = average_lengths[1] - average_lengths[0]
    z = (average_lengths[1] - average_lengths[0]) / abs(average_lengths[0])

    return x, y, z


# --------------------------------------------------------------------------------------


@task
def get_ideal_env_measure(path, distance_cutoff=1.4, angle_cutoff=0.3):
    
    # To see what I modeled this method after, look at...
    # https://github.com/materialsproject/crystaltoolkit/blob/a22839a71263a4734351e6e143a9c6cacba16a35/crystal_toolkit/components/localenv.py#L715
    
    
    # Let's run this within a supercell structure
    supercell_path = get_oxi_supercell_path(path, min_sl_v=7, oxi=True, new_oxi=True)

    images = supercell_path.get_structures(
        nimages=1,
        # vac_mode=True,  # vacancy mode
        idpp=True,
        # **idpp_kwargs,
        # species = 'Li', # Default is None. Set this if I only want one to move
    )
    # NOTE: the diffusion atom is always the first site in these structures (index=0)

    def get_valences(structure):
        valences = [getattr(site.specie, "oxi_state", None) for site in structure]
        valences = [v for v in valences if v is not None]
        if len(valences) == len(structure):
            return valences
        else:
            return "undefined"
        
    ideal_measures = []
    for image in images:
    
        lgf = LocalGeometryFinder()
        lgf.setup_structure(structure=image)
    
        se = lgf.compute_structure_environments(
            maximum_distance_factor=distance_cutoff + 0.01,
            only_indices=[0],  # only the diffusing ion
            valences=get_valences(image),
        )
        strategy = SimplestChemenvStrategy(
            distance_cutoff=distance_cutoff, angle_cutoff=angle_cutoff
        )
        lse = LightStructureEnvironments.from_structure_environments(
            strategy=strategy, structure_environments=se
        )
        
        csm_measure = lse.coordination_environments[0][0]["csm"]
        ideal_measures.append(csm_measure)
    
    # test with different measures
    alpha = ideal_measures[0]
    beta = ideal_measures[1] - ideal_measures[0]
    gamma = (ideal_measures[1] - ideal_measures[0]) / abs(ideal_measures[0])
    
    return alpha, beta, gamma

# --------------------------------------------------------------------------------------

# NOTE: if an entry already exists for this pathway, it is overwritten


@task(trigger=all_finished, max_retries=3, retry_delay=timedelta(seconds=5))
def add_empiricalmeasures_to_db(pathway_id, ewald_data, bondlen_data, csm_data):

    # unpack data from all my different versions above.
    a, b, c, d, e, f, g, h, i, j = ewald_data

    x, y, z = bondlen_data
    
    alpha, beta, gamma = csm_data

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
        ewald_energyg=g if not isinstance(g, Exception) else None,
        ewald_energyh=h if not isinstance(h, Exception) else None,
        ewald_energyi=i if not isinstance(i, Exception) else None,
        ewald_energyj=j if not isinstance(j, Exception) else None,
        #
        bond_lengthx=x if not isinstance(x, Exception) else None,
        bond_lengthy=y if not isinstance(y, Exception) else None,
        bond_lengthz=z if not isinstance(z, Exception) else None,
        #
        csm_alpha=alpha if not isinstance(alpha, Exception) else None,
        csm_beta=beta if not isinstance(beta, Exception) else None,
        csm_gamma=gamma if not isinstance(gamma, Exception) else None,
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
    bondlen_data = get_average_bond_length(pathway)
    csm_data = get_ideal_env_measure(pathway)

    # save the data to our database
    add_empiricalmeasures_to_db(pathway_id, ewald_data, bondlen_data, csm_data)

# for Prefect Cloud compatibility, set the storage to an import path
# workflow.storage = LocalStorage(path=f"{__name__}:workflow", stored_as_script=True)

# --------------------------------------------------------------------------------------
