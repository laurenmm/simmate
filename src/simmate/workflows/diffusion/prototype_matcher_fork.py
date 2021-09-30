# -*- coding: utf-8 -*-


# NOTES
# This is a fork of pymatgen.analysis.prototypes because we need to overwrite the
# outdated AFLOW_PROTOTYPE_LIBRARY data.
# I do this in a super lazy way, as I only update the structure, mineral name, and
# prototype id. Everything else is left as is (and therefore is inaccurate!)

# New import is...
# from simmate.workflows.diffusion.prototype_matcher_fork import AflowPrototypeMatcher
# This will print a shit ton of warnings.... thanks aflow


import os

from monty.serialization import loadfn

from pymatgen.analysis.structure_matcher import StructureMatcher

module_dir = os.path.dirname(os.path.abspath(__file__))

# THIS IS OVERWRITTEN BELOW BY JACKSUND
AFLOW_PROTOTYPE_LIBRARY_OLD = loadfn(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "aflow_prototypes.json")
)


############## NEW CODE -JACKSUND
from pymatgen.io.cif import CifParser


def load_cif(filename):
    cif = CifParser(
        filename,
        occupancy_tolerance=float("inf"),
    )
    key = list(cif.as_dict().keys())[0]
    data = cif.as_dict()[key]
    structure = cif.get_structures()[0]
    
    data["structure"] = structure

    # formula = data["_chemical_formula_sum"]
    # aflow_id = data["_aflow_proto"]
    # mineral_name = data["_chemical_name_mineral"]

    return data


# grab the first prototype from pymatgen's original implementation. I'm going
# use this as a template to insert the new prototypes.
template = AFLOW_PROTOTYPE_LIBRARY_OLD[0]

import os
import copy
AFLOW_PROTOTYPE_LIBRARY = []
for ciffile in os.listdir("cifs"):
    data = load_cif(os.path.join("cifs", ciffile))
    entry = copy.deepcopy(template)
    entry["snl"].structure = data["structure"]
    entry["tags"]["aflow"] = data["_aflow_proto"]
    entry["tags"]["mineral"] = data["_chemical_name_mineral"]
    AFLOW_PROTOTYPE_LIBRARY.append(entry)

############## END NEW CODE 


class AflowPrototypeMatcher:
    """
    This class will match structures to their crystal prototypes, and will
    attempt to group species together to match structures derived from
    prototypes (e.g. an A_xB_1-x_C from a binary prototype), and will
    give these the names the "-like" suffix.
    This class uses data from the AFLOW LIBRARY OF CRYSTALLOGRAPHIC PROTOTYPES.
    If using this class, please cite their publication appropriately:
    Mehl, M. J., Hicks, D., Toher, C., Levy, O., Hanson, R. M., Hart, G., & Curtarolo, S. (2017).
    The AFLOW library of crystallographic prototypes: part 1.
    Computational Materials Science, 136, S1-S828.
    http://doi.org/10.1016/j.commatsci.2017.01.017
    """

    def __init__(self, initial_ltol=0.2, initial_stol=0.3, initial_angle_tol=5):
        """
        Tolerances as defined in StructureMatcher. Tolerances will be
        gradually decreased until only a single match is found (if possible).
        Args:
            initial_ltol: fractional length tolerance
            initial_stol: site tolerance
            initial_angle_tol: angle tolerance
        """
        self.initial_ltol = initial_ltol
        self.initial_stol = initial_stol
        self.initial_angle_tol = initial_angle_tol

    @staticmethod
    def _match_prototype(structure_matcher, structure):
        tags = []
        for d in AFLOW_PROTOTYPE_LIBRARY:
            p = d["snl"].structure
            match = structure_matcher.fit_anonymous(p, structure)
            if match:
                tags.append(d)
        return tags

    def _match_single_prototype(self, structure):
        sm = StructureMatcher(
            ltol=self.initial_ltol,
            stol=self.initial_stol,
            angle_tol=self.initial_angle_tol,
        )
        tags = self._match_prototype(sm, structure)
        while len(tags) > 1:
            sm.ltol *= 0.8
            sm.stol *= 0.8
            sm.angle_tol *= 0.8
            tags = self._match_prototype(sm, structure)
            if sm.ltol < 0.01:
                break
        return tags

    def get_prototypes(self, structure):
        """
        Get prototype(s) structures for a given
        input structure. If you use this method in
        your work, please cite the appropriate
        AFLOW publication:
        Mehl, M. J., Hicks, D., Toher, C., Levy, O.,
        Hanson, R. M., Hart, G., & Curtarolo, S. (2017).
        The AFLOW library of crystallographic prototypes: part 1.
        Computational Materials Science, 136, S1-S828.
        http://doi.org/10.1016/j.commatsci.2017.01.017
        Args:
            structure: structure to match
        Returns (list): A list of dicts with keys
        'snl' for the matched prototype and 'tags',
        a dict of tags ('mineral', 'strukturbericht'
        and 'aflow') of that prototype. This should
        be a list containing just a single entry,
        but it is possible a material can match
        multiple prototypes.
        """

        tags = self._match_single_prototype(structure)

        if len(tags) == 0:
            return None
        return tags
