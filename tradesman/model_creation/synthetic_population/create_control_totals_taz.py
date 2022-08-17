import csv
from os.path import join
import pandas as pd
import pycountry
from aequilibrae.project import Project


def create_control_totals_taz(project: Project, model_place: str):

    # TODO: fix temporary folder path
    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3
    un_hh_size = pd.read_csv("")[country_code]

    zoning = project.zoning
    fields = zoning.fields

    selected_fields = []

    for field in fields:
        if "f_pop" in field:
            selected_fields.append(field)
        elif "m_pop" in field:
            selected_fields.append(field)

    df = df[selected_fields].copy()

    df["POPBASE"] = df[selected_fields].transpose().sum().tolist()

    df["HHBASE1"] = df["POPBASE"] / un_hh_size["AVGSIZE"] * un_hh_size["HHBASE1"]

    df["HHBASE2"] = df["POPBASE"] / un_hh_size["AVGSIZE"] * un_hh_size["HHBASE2"]

    df["HHBASE4"] = df["POPBASE"] / un_hh_size["AVGSIZE"] * un_hh_size["HHBASE4"]

    df["HHBASE6"] = df["POPBASE"] / un_hh_size["AVGSIZE"] * un_hh_size["HHBASE6"]

    df["HHBASE"] = df["HHBASE1"] + df["HHBASE2"] + df["HHBASE4"] + df["HHBASE6"]

    df = df.round(decimals=0).astype(int)

    df.insert(0, "TAZ")

    df["TAZ"] = list(range(1, len(df) + 1))

    taz_list = list(df.to_records(index=False))

    folder = r""

    with open(join(folder, "control_totals_taz.csv"), "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(df.columns.tolist())
        for zone in taz_list:
            writer.writerow(zone)
