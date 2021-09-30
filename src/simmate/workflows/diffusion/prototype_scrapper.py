# -*- coding: utf-8 -*-

import os
import urllib
from selenium import webdriver
import pandas as pd
from tqdm import tqdm
from pymatgen.core.composition import Composition

# IMPORTANT: to set up your web driver, make sure you installed chromium with...
#   sudo snap install chromium

# Prototype's that fail and should be downloaded manually:
#   AB2_hP9_162_ad_k V2N
#   AB_hP4_156_ab_ab CuI
#   A3B3C_hP14_176_h_h_c Tl(FeTe)3
#   AB_cP2_221_a_b H4N2O3
#   AB_mP32_14_4e_4e AsS
#   ABC2_oI8_44_a_a_c NaNO2
#   AB_oP8_62_c_c SiNi

# --------------------------------------------------------------------------------------

# This first section only serves to grab all AFLOW IDs and chemical formulas. 
# I wish I knew an easier way to do this other than webscraping with selenium...

# launch the webbrowser
driver = webdriver.Chrome(
    executable_path="/snap/bin/chromium.chromedriver"
)  # /snap/bin/chromium gives errors

# load the webpage
driver.get("http://www.aflowlib.org/prototype-encyclopedia/prototype_index.html")

# Grab the Table of data and it's rows
table = driver.find_element_by_id("myTable")
rows = table.find_elements_by_tag_name("tr")

# grab all the headers from the first row
# headers = [column.text for column in rows[0].find_elements_by_tag_name("th")]
# I don't like these headers so I write my own here.
headers = [
    "formula",
    "nelements",
    "nsites",
    "pearson_symbol",
    "struc_design",
    "prototype_id",
    "space_group_symbol",
    "space_group_number",
    "notes",
]

# now go through each row and grab all the data (skipping the first which is just
# the headers)
data = []
for row in tqdm(rows[1:]):

    # go through each column in this row and grab its data
    # NOTE: I actually only use the AFLOW ID here, because I pull all data from
    # the CIF later. There just doesn't seem to be an easy way to grab just
    # this column using Selenium
    row_data = []
    for column in row.find_elements_by_tag_name("td"):
        row_data.append(column.text)
    data.append(row_data)

# We have no need for selenium anymore so we can close the window
driver.close()

# The formulas don't match the CIF file naming, so I use pymatgen to reformat them
# For example, CCaO3 turns into CaCO3 here. Also some formulas we want to either
# leave alone or change to something specific, so we set those here.
special_cases = {
    "O": "O",
    }

for entry in data[1:]:
    current_formula = entry[0]
    
    if current_formula in special_cases:
        new_formula = special_cases[current_formula]
    else:
        try:  # some fail so we just keep these as-is. ex: (Mn,Fe)2O3
            new_formula = Composition(current_formula).reduced_formula
        except:
            new_formula = str(current_formula)

    entry[0] = new_formula
    
# make DataFrame from our list of data
dataframe = pd.DataFrame(data=data, columns=headers)

# --------------------------------------------------------------------------------------

# This section downloads all of the CIF files for us.

# NOTE: POSCARs load faster, but the CIF data is much easier to parse. Also some
# POSCAR fail to load into a pymatgen structure object due to misformatting

# make a directory to store all the CIF files in
os.mkdir("cifs")

# add POSCARs to each data row
for _, row_data in tqdm(dataframe.iterrows()):
    
    # The way they name URLs is wacky, so I iterate through a few different
    # versions until I get one that works
    possible_cif_urls = [
        f"http://www.aflowlib.org/prototype-encyclopedia/CIF/{row_data.prototype_id}.cif",
        f"http://www.aflowlib.org/prototype-encyclopedia/CIF/{row_data.prototype_id}.{row_data.formula}.cif",
        f"http://www.aflowlib.org/prototype-encyclopedia/CIF/{row_data.prototype_id}.alpha-{row_data.formula}.cif",
        f"http://www.aflowlib.org/prototype-encyclopedia/CIF/{row_data.prototype_id}.beta-{row_data.formula}.cif",
        f"http://www.aflowlib.org/prototype-encyclopedia/CIF/{row_data.prototype_id}.eta-{row_data.formula}.cif",
        ]
    
    # assume we aren't successful until proven otherwise 
    is_successful = False
    for cif_url in possible_cif_urls:
        try:
            # seleium struggles to download files because of the FileDownload dialog
            # that pops up here. So instead, I use urllib to grab the file and save
            # it to our computer.
            urllib.request.urlretrieve(cif_url, f"cifs/{row_data.prototype_id}.cif")
            
            # if this line worked, then we can break from this for-loop
            is_successful = True
            break
        except:
            continue
    
    if not is_successful:
        print(cif_url)
        print(f"FAILED {row_data.prototype_id} {row_data.formula}")

# --------------------------------------------------------------------------------------
