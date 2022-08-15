from os import uname
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

    df['POPBASE'] = df[selected_fields].transpose().sum().tolist()

    df["HHBASE1"] = un_hh_size['HHBASE1'] * un_hh_size['AVGSIZE'] * df['POPBASE']

    df["HHBASE2"] = un_hh_size['HHBASE2'] * un_hh_size['AVGSIZE'] * df['POPBASE']

    df["HHBASE4"] = un_hh_size['HHBASE4'] * un_hh_size['AVGSIZE'] * df['POPBASE']

    df["HHBASE6"] = un_hh_size['HHBASE6'] * un_hh_size['AVGSIZE'] * df['POPBASE']

    df['HHBASE'] = df['HHBASE1'] + df['HHBASE2'] + df['HHBASE4'] + df['HHBASE6']

    
    pass
