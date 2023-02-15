import os
from os.path import dirname, join

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib import cycler


def validate_non_controlled_vars(country_code: str, folder: str):
    """
    Validates the synthetic pooulation previously created, using non-controlled variables.

    Args:
         *model_place*:
         *folder*:

    """

    controls = pd.read_csv(join(dirname(__file__), "controls_and_validation/hh_composition_data_validation.csv"))

    controls = controls[controls.iso_code == country_code]

    controls.reset_index(drop=True, inplace=True)

    persons = pd.read_csv(os.path.join(folder, "output/synthetic_persons.csv"))

    households = pd.read_csv(os.path.join(folder, "output/synthetic_households.csv"))

    # Percentage of households with at least one person in age range

    hh_num = len(households)

    pp_under_15 = len(persons[persons.AGEP < 15].groupby("hh_id").count())

    pp_under_18 = len(persons[persons.AGEP < 18].groupby("hh_id").count())

    pp_under_20 = len(persons[persons.AGEP < 20].groupby("hh_id").count())

    pp_over_60 = len(persons[persons.AGEP >= 60].groupby("hh_id").count())

    pp_over_65 = len(persons[persons.AGEP >= 65].groupby("hh_id").count())

    print("Households with at least one member in the range (percentage)")
    print("found | expected")
    print("Under 15")
    print("{:.2f}".format(((pp_under_15 / hh_num) * 100)), " | ", controls.hh_with_under_15[0])
    print("Under 18")
    print("{:.2f}".format(((pp_under_18 / hh_num) * 100)), " | ", controls.hh_with_under_18[0])
    print("Under 20")
    print("{:.2f}".format(((pp_under_20 / hh_num) * 100)), " | ", controls.hh_with_under_20[0])
    print("Over 60")
    print("{:.2f}".format(((pp_over_60 / hh_num) * 100)), " | ", controls.hh_with_over_60[0])
    print("Over 65")
    print("{:.2f}".format(((pp_over_65 / hh_num) * 100)), " | ", controls.hh_with_over_65[0])

    # Percentage of households with at least one person in both age ranges

    list_hh = households[households.NP >= 2].hh_id.tolist()

    filter_15 = persons[(persons["hh_id"].isin(list_hh)) & (persons.AGEP < 15)].hh_id.unique().tolist()
    filter_15_60 = len(persons[(persons["hh_id"].isin(filter_15)) & (persons.AGEP >= 60)].hh_id.unique().tolist())
    filter_15_65 = len(persons[(persons["hh_id"].isin(filter_15)) & (persons.AGEP >= 65)].hh_id.unique().tolist())

    filter_18 = persons[(persons["hh_id"].isin(list_hh)) & (persons.AGEP < 18)].hh_id.unique().tolist()
    filter_18_60 = len(persons[(persons["hh_id"].isin(filter_18)) & (persons.AGEP >= 60)].hh_id.unique().tolist())
    filter_18_65 = len(persons[(persons["hh_id"].isin(filter_18)) & (persons.AGEP >= 65)].hh_id.unique().tolist())

    filter_20 = persons[(persons["hh_id"].isin(list_hh)) & (persons.AGEP < 20)].hh_id.unique().tolist()
    filter_20_60 = len(persons[(persons["hh_id"].isin(filter_20)) & (persons.AGEP >= 60)].hh_id.unique().tolist())
    filter_20_65 = len(persons[(persons["hh_id"].isin(filter_20)) & (persons.AGEP >= 65)].hh_id.unique().tolist())

    print("Households with members in age range (percentage)")
    print("found | expected")
    print("Under 15 and 60 years and older")
    print("{:.2f}".format((filter_15_60 / hh_num) * 100), " | ", controls.hh_with_under_15_over_60[0])
    print("Under 15 and 65 years and older")
    print("{:.2f}".format((filter_15_65 / hh_num) * 100), " | ", controls.hh_with_under_15_over_65[0])
    print("Under 18 and 60 years and older")
    print("{:.2f}".format((filter_18_60 / hh_num) * 100), " | ", controls.hh_with_under_18_over_60[0])
    print("Under 18 and 65 years and older")
    print("{:.2f}".format((filter_18_65 / hh_num) * 100), " | ", controls.hh_with_under_18_over_65[0])
    print("Under 20 and 60 years and older")
    print("{:.2f}".format((filter_20_60 / hh_num) * 100), " | ", controls.hh_with_under_20_over_60[0])
    print("Under 20 and 65 years and older")
    print("{:.2f}".format((filter_20_65 / hh_num) * 100), " | ", controls.hh_with_under_20_over_65[0])

    return "Non-controlled vars checked."


def validate_controlled_vars(fldr):
    region_yaml = join(fldr, "verification.yaml")

    plt.style.use("ggplot")
    plt.rcParams["lines.linewidth"] = 1.5
    plt.rcParams["axes.prop_cycle"] = cycler(color=["b", "g", "r", "y"])
    plt.rcParams["savefig.dpi"] = 200
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.constrained_layout.h_pad"] = 0.5
    plt.rcParams["figure.figsize"] = (8, 15)
    plt.rcParams["hist.bins"] = 25

    parameters = {}

    # ignore sys.argv if running validation notebook
    # is_script = "ipykernel" not in sys.modules

    # if is_script and len(sys.argv) > 1:
    #     if os.path.isfile(sys.argv[1]):
    #         region_yaml = sys.argv[1]

    with open(region_yaml) as f:
        parameters.update(yaml.safe_load(f))

    # if is_script and len(sys.argv) > 2:
    #     if os.path.isfile(sys.argv[2]):
    #         parameters_csv = sys.argv[2]
    #         parameters.update(pd.read_csv(parameters_csv, header=None, index_col=0, comment='#').to_dict()[1])

    # popsim_dir      = parameters.get('POPSIMDIR') or parameters.get('popsim_dir')
    validation_dir = parameters.get("VALID_DIR") or parameters.get("validation_dir")
    geography_file = parameters.get("geographies")
    use_geographies = parameters.get("group_geographies")
    summary_files = parameters.get("summaries", [])
    aggregate_list = parameters.get("aggregate_summaries", [])
    scenario = parameters.get("scenario")
    region = parameters.get("region")
    exp_hh_file = parameters.get("expanded_hhid")
    exp_hh_id_col = parameters.get("expanded_hhid_col")
    seed_hh_file = parameters.get("seed_households")
    seed_hh_cols = parameters.get("seed_cols")

    if not os.path.isdir(join(fldr, validation_dir)):
        os.mkdir(join(fldr, validation_dir))

    summary_df = pd.DataFrame()
    for summary_file in summary_files:
        filepath = os.path.join(fldr, summary_file)  # mudar popsimdir para fldr
        df = pd.read_csv(filepath)
        summary_df = pd.concat([summary_df, df])

    # summary_df.head()

    for geog in use_geographies:
        if geog not in summary_df.geography.unique():
            summary_df = pd.concat([summary_df, meta_geog_df(summary_df, geog, fldr, geography_file, use_geographies)])

    # summary_df.tail()

    fig_w = 3
    fig_l = int(len(aggregate_list) / fig_w) + 1

    summary_fig, axes = plt.subplots(fig_l, fig_w, figsize=(fig_w * 5, fig_l * 5))

    stats = []
    for params, ax in zip(aggregate_list, axes.ravel()):
        s, f, diff = process_control(summary_df, **params)
        stats.append(s)

        ax.set_title(f"{params['geography']} - {params['name']}")
        ax.set_ylabel("Frequency")
        ax.set_xlabel("Difference: control vs. result")
        ax.hist(diff, bins=10, range=(-5, 5), alpha=0.5)

    summary_fig.savefig(os.path.join(fldr, validation_dir, "frequencies.pdf"))
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv(os.path.join(fldr, validation_dir, f"{scenario}_{region}_popsim_stats.csv"), index=False)

    std_fig = plt.figure(figsize=(8, 15))
    std_fig.suptitle("PopulationSim Controls Percentage Difference")
    plt.errorbar(stats_df["mean_pc_difference"], stats_df["name"], xerr=stats_df["std"], linestyle="None", marker=".")

    std_fig.savefig(os.path.join(fldr, validation_dir, f"{scenario}_{region}_popsim_convergence_stdev.pdf"))

    # seed_cols = (seed_hh_cols.values())
    geog = seed_hh_cols.get("geog")
    geog_weight = seed_hh_cols.get("geog_weight")
    # hh_id = seed_hh_cols.get('hh_id')

    expanded_hhids = pd.read_csv(os.path.join(fldr, exp_hh_file), usecols=[exp_hh_id_col])  # popsim/fldr

    seed_hh_df = pd.read_csv(os.path.join(fldr, seed_hh_file), usecols=["PUMA", "WGTP", "hhnum"])  # popsim/fldr
    seed_hh_df.rename(columns={"hhnum": "hh_id"}, inplace=True)
    seed_hh_df.set_index(keys="hh_id", inplace=True)

    weight_mask = seed_hh_df[geog_weight] > 0
    weight = expanded_hhids[exp_hh_id_col].value_counts()[weight_mask]
    expansion_factor = (weight / seed_hh_df[geog_weight]).fillna(0)

    df = pd.DataFrame(
        {
            geog: seed_hh_df[geog],
            geog_weight: seed_hh_df[geog_weight],
            "weight": weight,
            "ef": expansion_factor,
        }
    )

    geog_group = df.groupby(geog)
    geog_final_weight = geog_group.sum()["weight"]
    expansion = geog_final_weight / geog_group.sum()[geog_weight]

    expansion.name = "avg_expansion"
    df = df.join(expansion, on=geog)
    df["diff_sq"] = (df["avg_expansion"] - df["ef"]) ** 2
    rmse = df.groupby(geog).mean()["diff_sq"] ** 0.5

    uniformity_df = pd.DataFrame(
        {
            "W": geog_group.sum()[geog_weight],
            "Z": geog_group.sum()["weight"],
            "N": geog_group.count()[geog_weight],
            "EXP": expansion,
            "EXP_MIN": geog_group.min()["ef"],
            "EXP_MAX": geog_group.max()["ef"],
            "RMSE": rmse,
        }
    )

    uniformity_df.to_csv(os.path.join(fldr, validation_dir, "uniformity.csv"))
    # uniformity_df

    geogs = df[geog].unique()
    geog_fig = plt.figure(figsize=(10 * len(geogs), 10))

    for i, g in enumerate(geogs):
        geog_df = df[df[geog] == g]
        counts, bins = np.histogram(geog_df["ef"])
        ax = geog_fig.add_subplot(1, len(geogs), i + 1)
        ax.set_title(f"{geog} {g}")
        ax.set_ylabel("Percentage")
        ax.set_xlabel("Expansion Factor Range")
        ax.hist(bins[:-1], bins, weights=counts * 100 / len(geog_df), alpha=0.6)


def meta_geog_df(summary_df, meta_geog, folder, geography_file, use_geographies):
    """
    This function creates a ____ for the upper level geography.


    """

    geography_df = pd.read_csv(os.path.join(folder, geography_file))
    geog = use_geographies[use_geographies.index(meta_geog) + 1]  # next geography in list
    meta_df = geography_df[[meta_geog, geog]].drop_duplicates(ignore_index=True)
    geog_df = summary_df[summary_df.geography == geog].copy()
    geog_df["geography"] = meta_geog
    geog_df["id"] = geog_df.id.map(meta_df.set_index(geog).to_dict()[meta_geog])

    return geog_df


def process_control(summary_df, name, geography, control, result):
    """
    Global
    ------
    summary_df: pandas DataFrame

    Parameters
    ----------
    name: str, output plot title
    geography: str, groupby geography
    control: str, control column name in summary table
    result: str, result column name in summary table

    Returns
    -------

    stats: pandas Series of statistics, aggregated by geography/control/result
    frequencies: pandas Series of control vs. results differences
    """

    sub_df = summary_df[summary_df.geography == geography][[control, result]].dropna(axis=0, how="any")

    observed = sub_df[control]
    non_zero_observed = observed[observed > 0]
    predicted = sub_df[result]
    difference = predicted - observed
    pc_difference = (difference / non_zero_observed) * 100
    rmse = (difference**2).mean() ** 0.5

    frequencies = non_zero_observed.groupby(difference).count()

    stats = pd.Series(
        {
            "name": name,
            "geography": geography,
            "observed": observed.sum(),
            "predicted": predicted.sum(),
            "difference": difference.sum(),
            "pc_difference": (difference.sum() / observed.sum()) * 100,
            "mean_pc_difference": pc_difference.mean(),
            "N": non_zero_observed.shape[0],
            "rmse": rmse,
            "std": pc_difference.std(),
        }
    )

    return stats, frequencies, difference
