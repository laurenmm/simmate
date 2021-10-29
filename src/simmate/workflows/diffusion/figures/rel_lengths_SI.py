# -*- coding: utf-8 -*-

nbins = 14

# --------------------------------------------------------------------------------------

from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import Relative
from django_pandas.io import read_frame

queryset1 = Relative.objects.filter(barrier=0).all()
df1 = read_frame(queryset1)

queryset2 = Relative.objects.filter(barrier__gt=0).all()
df2 = read_frame(queryset2)

# --------------------------------------------------------------------------------------


import numpy

count1, division1 = numpy.histogram(df1["length"], bins=nbins, range=(0, 1))
count2, division2 = numpy.histogram(df2["length"], bins=nbins, range=(0, 1))

total = count1 + count2
frac = count1 / total

division_mid = [
    (division1[i] + division1[i + 1]) / 2 for i, _ in enumerate(division1[:-1])
]

zero_pt = (
    Relative.objects.filter(length=0, barrier=0).count()
    / Relative.objects.filter(length=0).count()
)
division_mid = numpy.append(division_mid, 0)
frac = numpy.append(frac, zero_pt) * 100

# --------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

# start with a square Figure
fig = plt.figure(figsize=(4 * 1.68, 4))  # golden ratio = 1.618

# Add axes for the main plot
ax1 = fig.add_subplot(
    xlabel="$(L - L_{min}) / L_{min}$",
    ylabel=r"Number of Pathways (#)",
    xlim=(-0.05, 1.05),
    # ylim=(-0.05, 2),
)

# add the data as a scatter
hb = ax1.hist(
    x=[df1["length"], df2["length"]],  # X
    bins=nbins,
    range=(0, 1),
    color=["green", "silver"],
    edgecolor="white",
    linewidth=0.5,
    stacked=True,
)

ax2 = ax1.twinx()
ax2.set_ylabel("$E_{min}$ Pathways (%)")
hb = ax2.scatter(
    x=division_mid,
    y=frac,
    color="blue"
)

ax2.spines['right'].set_color('blue')
ax2.yaxis.label.set_color('blue')
ax2.tick_params(axis='y', colors='blue')

ax1.spines['left'].set_color('green')
ax2.spines['left'].set_color('green')
ax1.yaxis.label.set_color('green')
ax1.tick_params(axis='y', colors='green')

# plt.show()
plt.savefig("relative_length.svg", format="svg")

# --------------------------------------------------------------------------------------
