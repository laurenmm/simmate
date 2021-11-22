# -*- coding: utf-8 -*-

from simmate.shortcuts import setup
from simmate.database.diffusion import Pathway as Pathway_DB


queryset = (
    Pathway_DB.objects.filter(
        # vaspcalca__energy_barrier__isnull=False,
        vaspcalcb__energy_barrier__isnull=False,
    )
    .select_related("vaspcalca", "vaspcalcb", "empiricalmeasures", "structure")
    .all()
)
# .to_pymatgen().write_path("test.cif", nimages=3)
from django_pandas.io import read_frame

df = read_frame(
    queryset,
    fieldnames=[
        "id",
        "structure__id",
        "structure__formula_reduced",
        "structure__e_above_hull",
        "empiricalmeasures__dimensionality",
        # "vaspcalca__energy_barrier",
        "empcorbarrier__barrier",
        "vaspcalcb__energy_barrier",
    ],
    # column_names=[
    #     "pathway_id",
    #     "structure_id",
    #     "reduced_formula",
    #     "energy_above_hull",
    #     "pathway_dimensionality",
    #     "approx_barrier",
    #     "approx_barrier_corrected",
    #     "neb_barrier",
    # ],
)

df.to_csv("neb_calculated_pathways.csv", index=False)

# ----------------------------------------------------------------------------

queryset = (
    Pathway_DB.objects.filter(
        vaspcalca__energy_barrier__isnull=False,
    )
    .select_related("vaspcalca", "vaspcalcb", "empiricalmeasures", "structure")
    .all()
)
# .to_pymatgen().write_path("test.cif", nimages=3)
from django_pandas.io import read_frame

df2 = read_frame(
    queryset,
    fieldnames=[
        "id",
        "length",
        "atomic_fraction",
        "structure__id",
        "structure__nsites",
        "structure__nelement",
        "structure__density",
        "structure__spacegroup",
        "structure__formula_full",
        "structure__formula_reduced",
        "structure__chemical_system",
        "structure__formula_anonymous",
        "structure__e_above_hull",
        "structure__hostlattice__dimension",
        "structure__matprojdata2__band_gap",
        "structure__matprojdata2__cost_per_mol",
        "structure__matprojdata2__cost_per_kg",
        "structure__prototype2__name",
        "structure__prototype2__formula_reduced",
        "structure__prototype3__number",
        "empiricalmeasures__dimensionality",
        "empiricalmeasures__dimensionality_cumlengths",
        "empiricalmeasuresb__ewald_energyb",
        "empiricalmeasures__ionic_radii_overlap_cations",
        "empiricalmeasures__ionic_radii_overlap_anions",
        "relative__length",
        "relative__barrier",
        "vaspcalca__energy_barrier",
        "empcorbarrier__barrier",
        "vaspcalcb__energy_barrier",
    ],
    # column_names=[
    #     "pathway_id",
    #     "pathway_length",
    #     "atomic_fraction_fluoride",
    #     "structure_id",
    #     "number_of_sites",
    #     "number_of_elements",
    #     "density",
    #     "spacegroup",
    #     "full_formula",
    #     "formula_reduced",
    #     "chemical_system",
    #     "anonymous_formula",
    #     "energy_above_hull",
    #     "host_lattice_dimensionality",
    #     "materials_project_band_gap",
    #     "raw_element_cost_per_mol",
    #     "raw_element_cost_per_kg",
    #     "AFLOW_prototype_name",
    #     "AFLOW_protoype_reduced_formula",
    #     "anonymous_structure_type_id",
    #     "pathway_dimensionality",
    #     "pathway_dimensionality_w_shorter_paths",
    #     "delta_ewald_energy",
    #     "delta_iro_cations",
    #     "delta_iro_anions",
    #     "pathway_length_divided_shortest_in_structure",
    #     "barrier_minus_lowest_in_structure",
    #     "approx_barrier",
    #     "approx_barrier_corrected",
    #     "neb_barrier",
    # ],
)

df2.to_csv("all_calculated_pathways.csv", index=False)
