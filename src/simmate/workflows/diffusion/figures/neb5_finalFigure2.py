# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------

import json
import numpy

from simmate.configuration.django import setup_full  # ensures setup
from simmate.database.diffusion import Pathway as Pathway_DB

queryset = (
    Pathway_DB.objects.filter(
        # vaspcalcd__energysteps_midpoint_json__isnull=False,
        vaspcalcb__energy_barrier__isnull=False,
        # vaspcalcd__converged_start=True,
        # vaspcalcd__converged_midpoint=True,
        # vaspcalcd__converged_end=True,
    )
    .select_related(
        "vaspcalca", "vaspcalcd", "vaspcalcb", "empiricalmeasures", "structure"
    )
    .all()
)
from django_pandas.io import read_frame

df = read_frame(
    queryset,
    fieldnames=[
        "id",
        "length",
        "atomic_fraction",
        "nsites_777",
        "nsites_101010",
        "structure__e_above_hull",
        "empiricalmeasures__ewald_energy",
        "vaspcalcd__forces_start_json",
        "vaspcalcd__forces_midpoint_json",
        "vaspcalcd__forces_end_json",
        "vaspcalcd__stress_start_json",
        "vaspcalcd__stress_midpoint_json",
        "vaspcalcd__stress_end_json",
        "vaspcalcd__energysteps_start_json",
        "vaspcalcd__energysteps_midpoint_json",
        "vaspcalcd__energysteps_end_json",
        "vaspcalcd__timesteps_start_json",
        "vaspcalcd__timesteps_midpoint_json",
        "vaspcalcd__timesteps_end_json",
        "vaspcalcd__error_time_start",
        "vaspcalcd__error_time_midpoint",
        "vaspcalcd__error_time_end",
        "vaspcalcb__energy_barrier",
        "vaspcalca__energy_barrier",
    ],
)

## FORCES


def json_util(json_to_load):
    if json_to_load:
        return json.loads(json_to_load)
    else:
        return None


df["vaspcalcd__forces_start"] = df.vaspcalcd__forces_start_json.apply(json_util)
df["vaspcalcd__forces_midpoint"] = df.vaspcalcd__forces_midpoint_json.apply(json_util)
df["vaspcalcd__forces_end"] = df.vaspcalcd__forces_end_json.apply(json_util)

## STRESSES
df["vaspcalcd__stress_start"] = df.vaspcalcd__stress_start_json.apply(json_util)
df["vaspcalcd__stress_midpoint"] = df.vaspcalcd__stress_midpoint_json.apply(json_util)
df["vaspcalcd__stress_end"] = df.vaspcalcd__stress_end_json.apply(json_util)

## TIMES
df["vaspcalcd__timesteps_start"] = df.vaspcalcd__timesteps_start_json.apply(json_util)
df["vaspcalcd__timesteps_midpoint"] = df.vaspcalcd__timesteps_midpoint_json.apply(
    json_util
)
df["vaspcalcd__timesteps_end"] = df.vaspcalcd__timesteps_end_json.apply(json_util)

## ENERGIES FOR ALL IONIC STEPS
df["vaspcalcd__energysteps_start"] = df.vaspcalcd__energysteps_start_json.apply(
    json_util
)
df["vaspcalcd__energysteps_midpoint"] = df.vaspcalcd__energysteps_midpoint_json.apply(
    json_util
)
df["vaspcalcd__energysteps_end"] = df.vaspcalcd__energysteps_end_json.apply(json_util)


## ENERGIES
df["vaspcalcd__energysteps_barrier"] = [
    [max([m - s, m - e]) for s, m, e in zip(s_list, m_list, e_list)]
    if all([s_list, m_list, e_list])
    else None
    for s_list, m_list, e_list in zip(
        df.vaspcalcd__energysteps_start,
        df.vaspcalcd__energysteps_midpoint,
        df.vaspcalcd__energysteps_end,
    )
]
df["vaspcalcd__energysteps_barrier_errors"] = [
    [e - true_barrier for e in e_list] if e_list and true_barrier else None
    for e_list, true_barrier in zip(
        df.vaspcalcd__energysteps_barrier, df.vaspcalcb__energy_barrier
    )
]

# TOTAL TIMES AT EACH STEP
df["vaspcalcd__timesteps"] = [
    [sum([s, m, e]) for s, m, e in zip(s_list, m_list, e_list)]
    if all([s_list, m_list, e_list])
    else None
    for s_list, m_list, e_list in zip(
        df.vaspcalcd__timesteps_start,
        df.vaspcalcd__timesteps_midpoint,
        df.vaspcalcd__timesteps_end,
    )
]

# CONVERGENCE DATA
df["vaspcalcd__energysteps_start_convergence"] = [
    [abs(e_list[i + 1] - e_list[i]) for i in range(len(e_list) - 1)] if e_list else None
    for e_list in df.vaspcalcd__energysteps_start
]
df["vaspcalcd__energysteps_midpoint_convergence"] = [
    [abs(e_list[i + 1] - e_list[i]) for i in range(len(e_list) - 1)] if e_list else None
    for e_list in df.vaspcalcd__energysteps_midpoint
]
df["vaspcalcd__energysteps_end_convergence"] = [
    [abs(e_list[i + 1] - e_list[i]) for i in range(len(e_list) - 1)] if e_list else None
    for e_list in df.vaspcalcd__energysteps_end
]

# Normalizing forces
def numpy_util(data):
    if data:
        return [numpy.linalg.norm(step) for step in data]
    else:
        return numpy.NAN


df["vaspcalcd__forces_norm_start"] = df.vaspcalcd__forces_start.apply(numpy_util)
df["vaspcalcd__forces_norm_midpoint"] = df.vaspcalcd__forces_midpoint.apply(numpy_util)
df["vaspcalcd__forces_norm_end"] = df.vaspcalcd__forces_end.apply(numpy_util)

# This is useful a couple places below
df["error_static"] = [
    pathway_barriers[0] if pathway_barriers else numpy.NAN
    for pathway_barriers in df.vaspcalcd__energysteps_barrier_errors
]

# N_SITES Experimental
df["nsites_777_^-3"] = df.nsites_777.apply(lambda x: x ** -(1 / 3))

# --------------------------------------------------------------------------------------

# This section grabs data from vaspcalcd that represents EDIFFG=0.1, NSW=10
convergence = 0.1
max_nsw = 8

# for testing
steps_required_to_converge = []
times = []

for image in ["start", "midpoint", "end"]:
    energies = []
    forces = []
    for energysteps, convsteps, forcesteps, timesteps in zip(
        df[f"vaspcalcd__energysteps_{image}"],
        df[f"vaspcalcd__energysteps_{image}_convergence"],
        df[f"vaspcalcd__forces_norm_{image}"],
        df["vaspcalcd__timesteps"],
    ):
        if not all([energysteps, convsteps]):
            energies.append(None)
            forces.append(None)
            continue
        for i, c in enumerate(convsteps):
            if c <= convergence or i >= max_nsw:  # <<< This is where I set limits
                steps_required_to_converge.append(i)
                break
        if c >= convergence:
            print(c, convergence)  # !!! THIS WILL REPORT ANY UNCONVERGED CALCS
        energies.append(energysteps[i + 1])
        forces.append(forcesteps[i + 1])
        times.append(sum(forcesteps[: i + 1]))
    df[f"energy_{image}_{convergence}"] = energies
    df[f"force_{image}_{convergence}"] = forces

barriers = []
errors = []
forces = []

for s, m, e, fs, fm, fe, actual in zip(
    df[f"energy_start_{convergence}"],
    df[f"energy_midpoint_{convergence}"],
    df[f"energy_end_{convergence}"],
    df[f"force_start_{convergence}"],
    df[f"force_midpoint_{convergence}"],
    df[f"force_end_{convergence}"],
    df["vaspcalcb__energy_barrier"],
):
    if not all([s, m, e, fs, fm, fe, actual]):
        forces.append(None)
        barriers.append(None)
        errors.append(None)
        continue
    force_diff = max([fm - fs, fm - fe])
    forces.append(force_diff)
    barrier = max([m - s, m - e])
    barriers.append(barrier)
    errors.append(barrier - actual)

df[f"force_{convergence}"] = forces
df[f"barrier_{convergence}"] = barriers
df[f"error_{convergence}"] = errors

# --------------------------------------------------------------------------------------

# ERROR STATS AND OUTLIER DETECTION

# For the static calcs
all_errors_static = df["error_static"].dropna().to_numpy()
median_error_static = numpy.median(all_errors_static)
std_error_static = numpy.std(all_errors_static)
df["is_outlier_static"] = [
    bool(abs(error - median_error_static) > (3 * std_error_static))
    for error in df["error_static"]
]
print(
    f"The error (median +/- stdev) for STATIC: {median_error_static} +/- {std_error_static}"
)

# For the relax dataset
all_errors = df[f"error_{convergence}"].dropna().to_numpy()
median_error_relax = numpy.median(all_errors)
std_error_relax = numpy.std(all_errors)
df[f"is_outlier_{convergence}"] = [
    bool(abs(error - median_error_relax) > (3 * std_error_relax))
    for error in df[f"error_{convergence}"]
]
print(
    f"The error (median +/- stdev) for RELAX: {median_error_relax} +/- {std_error_relax}"
)

# UNCOMMENT IF YOU WANT TO REMOVE!
# df = df[df["is_outlier_static"] == False]
# df = df[df[f"is_outlier_{convergence}"] == False]

# --------------------------------------------------------------------------------------

# LINEAR REGRESSION FOR STATIC AND RELAX

from sklearn import linear_model
from sklearn.model_selection import train_test_split

reg_static = linear_model.LinearRegression()
fields_to_fit = ["vaspcalca__energy_barrier"]
data = df[fields_to_fit + ["vaspcalcb__energy_barrier"]].dropna()
X_train = data[fields_to_fit]
y_train = data["vaspcalcb__energy_barrier"]
reg_static.fit(X_train, y_train)
print(
    list(reg_static.coef_) + [reg_static.intercept_]
)  # List of coefficients for each field
print(reg_static.score(X_train, y_train))  # R^2

reg_relax = linear_model.LinearRegression()
fields_to_fit = [f"barrier_{convergence}"]
data = df[fields_to_fit + ["vaspcalcb__energy_barrier"]].dropna()
X_train = data[fields_to_fit]
y_train = data["vaspcalcb__energy_barrier"]
reg_relax.fit(X_train, y_train)
print(
    list(reg_relax.coef_) + [reg_relax.intercept_]
)  # List of coefficients for each field
print(reg_relax.score(X_train, y_train))  # R^2


# --------------------------------------------------------------------------------------

# EMPIRICAL CORRECTION FOR STATIC

from sklearn import linear_model
from sklearn.model_selection import train_test_split

reg_static_emp = linear_model.LinearRegression()
# reg = linear_model.Lasso(alpha=0.1)

# split our dataframe into training and test sets
# df_training, df_test = train_test_split(df, test_size=0.2)
# df_training = df[df["is_outlier_static"] == False]

# Fields to use in fitting
fields_to_fit = [
    "vaspcalca__energy_barrier",
    "nsites_777_^-3",
]

data = df[fields_to_fit + ["vaspcalcb__energy_barrier"]].dropna()

X_train = data[fields_to_fit]
y_train = data["vaspcalcb__energy_barrier"]
reg_static_emp.fit(X_train, y_train)
print(
    list(reg_static_emp.coef_) + [reg_static_emp.intercept_]
)  # List of coefficients for each field
print(reg_static_emp.score(X_train, y_train))  # R^2


# Now use our test set to see how the model does
X_test = data[fields_to_fit]
y_test1_expected = data["vaspcalcb__energy_barrier"]
y_test1_predicted = reg_static_emp.predict(X_test)
y_test1_errors = y_test1_predicted - y_test1_expected
y_test1_std = numpy.std(y_test1_errors)
y_test1_median = numpy.median(y_test1_errors)
print(
    f"The error (median +/- stdev) for STATIC+EMP: {y_test1_median} +/- {y_test1_std}"
)

# --------------------------------------------------------------------------------------

# EMPIRICAL CORRECTION FOR PARTIAL RELAX

from sklearn import linear_model
from sklearn.model_selection import train_test_split

reg_relax_emp = linear_model.LinearRegression()
# reg = linear_model.Lasso(alpha=0.1)

# split our dataframe into training and test sets
# df_training, df_test = train_test_split(df, test_size=0.2)
# df_training = df[df[f"is_outlier_{convergence}"] == False]

# Fields to use in fitting
fields_to_fit = [
    f"barrier_{convergence}",
    f"force_{convergence}",
    "nsites_777_^-3",
]

data = df[fields_to_fit + ["vaspcalcb__energy_barrier"]].dropna()

X_train = data[fields_to_fit]
y_train = data["vaspcalcb__energy_barrier"]
reg_relax_emp.fit(X_train, y_train)
print(
    list(reg_relax_emp.coef_) + [reg_relax_emp.intercept_]
)  # List of coefficients for each field
print(reg_relax_emp.score(X_train, y_train))  # R^2


# Now use our test set to see how the model does
X_test = data[fields_to_fit]
y_test2_expected = data["vaspcalcb__energy_barrier"]
y_test2_predicted = reg_relax_emp.predict(X_test)
y_test2_errors = y_test2_predicted - y_test2_expected
y_test2_std = numpy.std(y_test2_errors)
y_test2_median = numpy.median(y_test2_errors)
print(
    f"The error (median +/- stdev) for STATIC+EMP: {y_test2_median} +/- {y_test2_std}"
)

# --------------------------------------------------------------------------------------


def add_reg_plot(ax, reg, stddev, color, center_reg):

    x = numpy.array([-10, 1, 10])
    if center_reg:
        m = reg.coef_[0]
        b = reg.intercept_
        y = m * x + b
        ax.plot(x, y, c=color)
    else:
        m = 1
        b = 0
        y = x.copy()

    # For specifying the distance between two parallel lines,
    # I use this link and solve for b2:
    # https://en.wikipedia.org/wiki/Distance_between_two_parallel_lines
    # In this equation, d is my standard deviation.
    # I also use 1*stdev because I want 1 deviations
    b_pos = b + 1 * stddev * numpy.sqrt(m ** 2 + 1)
    b_neg = b - 1 * stddev * numpy.sqrt(m ** 2 + 1)
    # print(f"A: {m} {b}")
    # print(f"b: {m} {b_pos}")
    # print(f"{stddev}")

    ax.plot(x, x * m + b_pos, c=color, linestyle="dashed")
    ax.plot(x, x * m + b_neg, c=color, linestyle="dashed")

    # this is the black y=mx line
    ax.plot(x, x, c="Black")


import matplotlib.pyplot as plt

# start with a square Figure
fig = plt.figure(figsize=(6, 6))  # golden ratio = 1.618

gs = fig.add_gridspec(
    # grid dimensions and column/row relative sizes
    nrows=2,
    ncols=2,
    # width_ratios=(1, 1, 1),
    # height_ratios=(1, 1, 1),
    #
    # size of the overall grid (all axes together)
    left=0.1,
    right=0.9,
    bottom=0.1,
    top=0.9,
    #
    # spacing between subplots (axes)
    wspace=0.0,
    hspace=0.0,
)

# First plot is just the approximated barriers
ax1 = fig.add_subplot(
    gs[0, 0],
    xlabel="Barrier (eV) [static]",
    ylabel=r"Midpoint-only NEB Barrier (eV)",
    xlim=(-1.5, 5),
    ylim=(-1.5, 5),
)
ax1.xaxis.set_ticks([-1,0,1,2,3,4,5])
hb = ax1.scatter(
    x=df["vaspcalca__energy_barrier"],  # X
    y=df["vaspcalcb__energy_barrier"],  # Y
    c="Green",  # COLOR
    alpha=0.4,  # Transparency
)
# hb = ax1.hexbin(
#     x=df["vaspcalca__energy_barrier"],  # X
#     y=df["vaspcalcb__energy_barrier"],  # Y
#     gridsize=10,  # size of hex bins
#     # cmap="RdYlGn_r",  # color scheme for colorbar
#     vmin=0,
#     # vmax=7.5,  # upper limit of colorbar
#     edgecolor="black",  # color between hex bins
# )
add_reg_plot(ax1, reg_static, std_error_static, "Green", True)


# 2nd plot is the empirically-corrected vaspcalca
ax2 = fig.add_subplot(
    gs[0, 1],
    xlabel="Barrier (eV) [static+ec]",
    sharex=ax1,
    sharey=ax1,
)
plt.setp(ax2.get_yticklabels(), visible=True)
hb = ax2.scatter(
    x=y_test1_predicted,  # X
    y=y_test1_expected,  # Y
    c="Blue",  # COLOR
    alpha=0.4,  # Transparency
)
add_reg_plot(ax2, reg_static_emp, y_test1_std, "Blue", False)


# 3rd plot is the partial relaxation
ax3 = fig.add_subplot(
    gs[1, 0],
    xlabel=f"Barrier (eV) [NSW={max_nsw}; EDIFFG={convergence}]",
    sharex=ax1,
    sharey=ax1,
)
plt.setp(ax3.get_yticklabels(), visible=True)
hb = ax3.scatter(
    x=df[f"barrier_{convergence}"],  # X
    y=df["vaspcalcb__energy_barrier"],  # Y
    c="Red",  # COLOR
    alpha=0.4,  # Transparency
)
add_reg_plot(ax3, reg_relax, std_error_relax, "Red", True)


# 4th plot is the empirically-corrected partial relaxation
ax4 = fig.add_subplot(
    gs[1, 1],
    xlabel="Approximated Barrier (eV) [relax+ec]",
    sharex=ax1,
    sharey=ax1,
)
plt.setp(ax4.get_yticklabels(), visible=True)
hb = ax4.scatter(
    x=y_test2_predicted,  # X
    y=y_test2_expected,  # Y
    c="Black",  # COLOR
    alpha=0.4,  # Transparency
)
add_reg_plot(ax4, reg_relax_emp, y_test2_std, "Black", False)

# plt.show()
plt.savefig("scatter.svg", format="svg")

# --------------------------------------------------------------------------------------

# calculate errors
static_errors = df["vaspcalca__energy_barrier"] - df["vaspcalcb__energy_barrier"]

import matplotlib.pyplot as plt

# start with a overall Figure canvas
fig = plt.figure(figsize=(6, 5))  # golden ratio = 1.618

# Add a gridspec (which sets up a total of 3 subplots for us -- stacked on one another)
gs = fig.add_gridspec(
    # grid dimensions and column/row relative sizes
    nrows=4,
    ncols=1,
    # width_ratios=(1, 1, 1),
    # height_ratios=(1, 1, 1),
    #
    # size of the overall grid (all axes together)
    left=0.1,
    right=0.9,
    bottom=0.1,
    top=0.9,
    #
    # spacing between subplots (axes)
    wspace=0.05,
    hspace=0.0,
)

range_for_bins = (-1.0, 1.0)

# Static
ax1 = fig.add_subplot(
    gs[0, 0],
    xlabel=r"Barrier Error vs. NEB (eV)",
)
hb = ax1.hist(
    x=static_errors,  # X
    bins=15,
    range=range_for_bins,
    color="Green",
    edgecolor="white",
    linewidth=0.5,
)

# Static + Empirical correction
ax2 = fig.add_subplot(
    gs[1, 0],
    xlabel=r"Barrier Error vs. NEB (eV)",
    ylabel=r"Pathways (#)",
    sharex=ax1,
    sharey=ax1,
)
hb = ax2.hist(
    x=y_test1_errors,
    bins=15,
    range=range_for_bins,
    color="Blue",
    edgecolor="white",
    linewidth=0.5,
)

# Relax
ax3 = fig.add_subplot(
    gs[2, 0],
    xlabel=r"Barrier Error vs. NEB (eV)",
    sharex=ax1,
    sharey=ax1,
)
hb = ax3.hist(
    x=df[f"error_{convergence}"],
    bins=15,
    range=range_for_bins,
    color="Red",
    edgecolor="white",
    linewidth=0.5,
)

# Relax + Empirical Correction
ax4 = fig.add_subplot(
    gs[3, 0],
    xlabel=r"Barrier Error vs. NEB (eV)",
    sharex=ax1,
    sharey=ax1,
)
# add histogram
hb = ax4.hist(
    x=y_test2_errors,  # X
    bins=15,
    range=range_for_bins,
    color="Black",
    edgecolor="white",
    linewidth=0.5,
)

# add vertical lines
for ax in [ax1, ax2, ax3, ax4]:
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")

# plt.show()
plt.savefig("hist.svg", format="svg")

# --------------------------------------------------------------------------------------


# TESTING

# from sklearn import linear_model
# from sklearn.model_selection import train_test_split

# # df = df[df["is_outlier_static"] == False]
# df = df[df[f"is_outlier_{convergence}"] == False]

# coefs = []
# intercepts = []
# r2s = []

# for trial in range(1000):

#     reg = linear_model.LinearRegression()
#     # reg = linear_model.Lasso(alpha=0.1)
#     # fit_intercept=False

#     # split our dataframe into training and test sets
#     df_training, df_test = train_test_split(df, test_size=0.5)

#     # Fields to use in fitting
#     fields_to_fit = [
#         # "vaspcalca__energy_barrier",
#         f"barrier_{convergence}",
#         "nsites_777_^-3",
#         # "length",
#         # "nsites_777",
#         f"force_{convergence}",
#         # "structure__e_above_hull",
#         # "empiricalmeasures__ewald_energy",

#     ]

#     data = df_training[fields_to_fit + ["vaspcalcb__energy_barrier"]].dropna()

#     X_train = data[fields_to_fit]
#     y_train = data["vaspcalcb__energy_barrier"]
#     reg.fit(X_train, y_train)
#     coefs.append(reg.coef_)  # List of coefficients for each field
#     r2s.append(reg.score(X_train, y_train))  # R^2
#     intercepts.append(reg.intercept_)

# %varexp --hist r2s
# %varexp --hist intercepts

# for n in range(len(fields_to_fit)):
#     aa = [i[n] for i in coefs]
#     %varexp --hist aa

# ----------------------------------------------------------------------------
