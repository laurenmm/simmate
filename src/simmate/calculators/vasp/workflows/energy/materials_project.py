# -*- coding: utf-8 -*-

from simmate.workflow_engine.utilities import s3task_to_workflow
from simmate.calculators.vasp.tasks.energy.materials_project import (
    MatProjStaticEnergy as MPStaticEnergyTask,
)
from simmate.calculators.vasp.database.energy import (
    MatProjStaticEnergy as MPStaticEnergyResults,
)

workflow = s3task_to_workflow(
    name="Materials Project Static Energy",
    module=__name__,
    project_name="Simmate-Energy",
    s3task=MPStaticEnergyTask,
    calculation_table=MPStaticEnergyResults,
    register_kwargs=["prefect_flow_run_id", "structure", "source"],
)
