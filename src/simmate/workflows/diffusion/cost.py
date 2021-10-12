# -*- coding: utf-8 -*-

from pymatgen.core.composition import Composition
from pymatgen.analysis.cost import CostDBElements, CostAnalyzer

comp = Composition("PbF3")

costs = CostDBElements()
a = CostAnalyzer(costs)

a.get_cost_per_kg(comp)

