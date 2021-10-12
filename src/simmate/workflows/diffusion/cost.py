# -*- coding: utf-8 -*-

from pymatgen.core.composition import Composition
from pymatgen.analysis.cost import CostDBElements, CostAnalyzer, CostDBCSV

comp = Composition("PbF3")

costs = CostDBElements()
# a = CostAnalyzer(costs) ## Fluoride cost is super misleading
a = CostDBCSV("costdb_elements.csv"")

a.get_cost_per_kg(comp)
