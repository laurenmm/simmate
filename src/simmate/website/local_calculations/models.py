# -*- coding: utf-8 -*-

# I store all of my models elsewhere, so this file simply exists to show django where
# they are located at. I do this based on the directions given by:
# https://docs.djangoproject.com/en/3.1/topics/db/models/#organizing-models-in-a-package

# Consider moving base_data_types to a separate app
from simmate.database.base_data_types.symmetry import Spacegroup

# Rather than retyping all of the logic from this file, I use the copy method here.
from simmate.database.local_calculations import *
