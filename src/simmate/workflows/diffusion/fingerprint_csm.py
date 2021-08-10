# -*- coding: utf-8 -*-

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

from pymatgen.core import Structure
structure = Structure.from_file("Ho2CF2_mp-9006_primitive.cif")


def get_chemenv_analysis(structure, distance_cutoff=1.4, angle_cutoff=0.3):

    def get_valences(structure):
        valences = [getattr(site.specie, "oxi_state", None) for site in structure]
        valences = [v for v in valences if v is not None]
        if len(valences) == len(structure):
            return valences
        else:
            return "undefined"

    # decide which indices to present to user
    sga = SpacegroupAnalyzer(structure)
    symm_structure = sga.get_symmetrized_structure()
    inequivalent_indices = [
        indices[0] for indices in symm_structure.equivalent_indices
    ]
    wyckoffs = symm_structure.wyckoff_symbols

    lgf = LocalGeometryFinder()
    lgf.setup_structure(structure=structure)

    se = lgf.compute_structure_environments(
        maximum_distance_factor=distance_cutoff + 0.01,
        only_indices=inequivalent_indices,
        valences=get_valences(structure),
    )
    strategy = SimplestChemenvStrategy(
        distance_cutoff=distance_cutoff, angle_cutoff=angle_cutoff
    )
    lse = LightStructureEnvironments.from_structure_environments(
        strategy=strategy, structure_environments=se
    )
    
    return lse

lse = get_chemenv_analysis(structure)
print(lse.coordination_environments)
