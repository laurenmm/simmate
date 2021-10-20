# -*- coding: utf-8 -*-

from tqdm import tqdm
from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import Pathway as Pathway_DB, EmpCorBarrier

queryset = (
    Pathway_DB.objects.filter(
        vaspcalca__energy_barrier__isnull=False,
    )
    .select_related("vaspcalca")
    .all()
)



orig=[]
new=[]
for pathway in tqdm(queryset):
    
    energy = pathway.vaspcalca.energy_barrier
    
    corrected_energy = energy * 0.549 + 0.119
    
    orig.append(energy)
    new.append(corrected_energy)
    
    ecb = EmpCorBarrier(barrier=corrected_energy, pathway=pathway)
    ecb.save()
