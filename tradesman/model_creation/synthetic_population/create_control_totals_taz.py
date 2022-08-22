import csv
from os.path import join
import pandas as pd
import geopandas as gpd
import pycountry
from aequilibrae.project import Project


def create_control_totals_taz(project: Project, model_place: str, file_folder: str):

    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3
    un_hh_size = pd.read_csv(r"tradesman\model_creation\synthetic_population\controls_and_validation\hh_size_data.csv")

    un_hh_size = un_hh_size[un_hh_size.iso_code == country_code]

    un_hh_size.reset_index(drop=True, inplace=True)

    df = pd.read_sql("SELECT * FROM zones;", con=project.conn)

    selected_fields = []

    for field in df.columns.tolist():
        if "POP" in field:
            selected_fields.append(field)

    df = df[selected_fields].copy()

    df["POPBASE"] = df[selected_fields].transpose().sum().tolist()

    df["HHBASE1"] = df["POPBASE"] / un_hh_size.AVGSIZE[0] * un_hh_size.HHBASE1[0] / 100

    df["HHBASE2"] = df["POPBASE"] / un_hh_size.AVGSIZE[0] * un_hh_size.HHBASE2[0] / 100

    df["HHBASE4"] = df["POPBASE"] / un_hh_size.AVGSIZE[0] * un_hh_size.HHBASE4[0] / 100

    df["HHBASE6"] = df["POPBASE"] / un_hh_size.AVGSIZE[0] * un_hh_size.HHBASE6[0] / 100

    df = df.round(decimals=0).astype(int)

    df["HHBASE"] = df["HHBASE1"] + df["HHBASE2"] + df["HHBASE4"] + df["HHBASE6"]

    df.insert(0, "TAZ", 0)

    df["TAZ"] = list(range(1, len(df) + 1))

    sql = "SELECT country_name, division_name, level, Hex(ST_AsBinary(GEOMETRY)) as geom FROM political_subdivisions WHERE level=1;"

    subdivisions = gpd.GeoDataFrame.from_postgis(sql, project.conn, geom_col="geom", crs=4326)

    sql = "SELECT zone_id, Hex(ST_AsBinary(geometry)) as geom FROM zones;"

    zones = gpd.GeoDataFrame.from_postgis(sql, con=project.conn, geom_col="geom", crs=4326)

    zones["centroid"] = zones.to_crs(3857).centroid.to_crs(4326)

    zones.set_geometry(col="centroid", drop=True, inplace=True)

    df["PUMA"] = 1

    df["REGION"] = 1

    df["MAZ"] = df.TAZ.tolist()

    df["xTAZ"] = gpd.sjoin(zones, subdivisions).index_right.tolist()

    df["xTAZ"] = df["xTAZ"] + 1

    df.to_csv(join(file_folder, "data/control_totals_taz.csv"), sep=",", index=False, index_label=None)

    print("control_totals_taz.csv file created.")
