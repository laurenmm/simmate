# -*- coding: utf-8 -*-

from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import Pathway as Pathway_DB

queryset = (
    Pathway_DB.objects.filter(
        vaspcalca__energy_barrier__isnull=False,
        vaspcalca__energy_barrier__gte=0,
        empiricalmeasures__ionic_radii_overlap_anions__gt=-900,
        # empiricalmeasuresb__ewald_energyb__gte=6,
        # empiricalmeasuresb__ewald_energyb__lte=-3,
        # length__gte=4.25,
        # length__lte=4.75,
    )
    .select_related("vaspcalca", "empiricalmeasuresb", "empcorbarrier")
    .all()
)
from django_pandas.io import read_frame

df = read_frame(
    queryset,
    fieldnames=[
        "length",
        "empiricalmeasuresb__ewald_energyb",
        "empiricalmeasures__ionic_radii_overlap_anions",
        "empiricalmeasures__ionic_radii_overlap_cations",
        "vaspcalca__energy_barrier",
        "empcorbarrier__barrier",
    ],
)

import numpy
from sklearn import linear_model
from sklearn.model_selection import train_test_split

linear_reg = linear_model.LinearRegression()
fields_to_fit = [
    "length",
    "empiricalmeasuresb__ewald_energyb",
    "empiricalmeasures__ionic_radii_overlap_anions",
    "empiricalmeasures__ionic_radii_overlap_cations",
]
data = df[fields_to_fit + ["empcorbarrier__barrier"]].dropna()

data_train, data_test = train_test_split(data, train_size=0.75)


X_train = data_train[fields_to_fit]
y_train = data_train["empcorbarrier__barrier"]
linear_reg.fit(X_train, y_train)
print(
    list(linear_reg.coef_) + [linear_reg.intercept_]
)  # List of coefficients for each field
print(linear_reg.score(X_train, y_train))  # R^2

# Now use our test set to see how the model does
X_test = data_test[fields_to_fit]
y_test_expected = data_test["empcorbarrier__barrier"]
y_test_predicted = linear_reg.predict(X_test)
y_test_errors = y_test_predicted - y_test_expected
y_test_std = numpy.std(y_test_errors)
y_test_median = numpy.median(y_test_errors)
print(
    f"The error (median +/- stdev) for STATIC+EMP: {y_test_median} +/- {y_test_std}"
)

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.hist(list(y_test_errors), 30, density=True, range=(-2.5,2.5), color="green")
plt.show()

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.scatter(y_test_predicted, y_test_expected, c="green", alpha=0.5)
ax.set_xlim(0,10)
ax.set_ylim(0,10)
x = numpy.array([-10, 1, 10])
ax.set_xlabel("Predicted (eV)")
ax.set_ylabel("Eapprox (corrected) (eV)")
ax.plot(x, x, c="Black")
plt.show()
