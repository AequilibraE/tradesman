import geopandas as gpd
import pandas as pd
from aequilibrae import Project
import pycountry

from tradesman.data.load_zones import load_zones
from tradesman.data.population_raster import population_raster


def get_pop_by_sex_age(project: Project, model_place: str):

    url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2000_2020/2020/"
    sex = ["f", "m"]
    age = [0, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    zoning = project.zoning
    fields = zoning.fields

    zones = load_zones(project)

    for s in sex:
        for a in range(len(age)):

            data_link = url + f"{country_code}/{country_code.lower()}_{s}_{age[a]}_2020.tif"
            field_name = f"{s}_pop_{age[a]}"

            try:
                df = population_raster(data_link, field_name, project)
            except:
                continue

            gdf_pop = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326)

            pop_per_zone = zones.sjoin(gdf_pop).groupby("zone_id").sum().astype(int)

            pop_per_zone.reset_index(inplace=True)

            list_of_tuples = list(pop_per_zone[["population", "index"]].itertuples(index=False, name=None))

            if age[a] < 80:
                fields.add(field_name, f"{s} population {age[a]} to {age[a+1]} years old.", "INTEGER")
            else:
                fields.add(field_name, f"{s} population over {age[a]} years old.", "INTEGER")

            project.conn.executemany(f"UPDATE zones SET {field_name}=? WHERE zone_id=?;", list_of_tuples)
            project.conn.commit()

            project.conn.execute(f"UPDATE zones SET {field_name}=0 WHERE {field_name} IS NULL;")
            project.conn.commit()

            print(f"Obtained {s} population aged {age[a]} years old.")
