import geopandas as gpd
import pycountry
from aequilibrae import Project

from tradesman.data.load_zones import load_zones
from tradesman.data.population_raster import population_raster


def get_pop_by_sex_age(project: Project, country_name: str):
    """
    Imports population by sex and age into the model.

    Parameters:
        *project*(:obj:`aequilibrae.project`): currently open project
        *country_name*(:obj:`str`): model place country
    """
    url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2000_2020/2020/"
    sex = ["f", "m"]
    age = [0, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
    country_code = pycountry.countries.search_fuzzy(country_name)[0].alpha_3

    zoning = project.zoning
    fields = zoning.fields

    zones = load_zones(project)

    for s in sex:
        for a in range(len(age)):
            data_link = url + f"{country_code}/{country_code.lower()}_{s}_{age[a]}_2020.tif"
            field_name = f"POP{s.upper()}{a+1}"

            df = population_raster(data_link, field_name=f"{country_code}_{field_name}", project=project)

            gdf_pop = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326)

            pop_per_zone = zones.sjoin(gdf_pop).groupby("zone_id").sum(numeric_only=True).astype(int)

            pop_per_zone.reset_index(inplace=True)

            list_of_tuples = list(pop_per_zone[["population", "zone_id"]].itertuples(index=False, name=None))

            preffix = "" if s == "m" else "fe"
            if age[a] < 80:
                fields.add(field_name, f"{preffix}male population {age[a]} to {age[a+1]} years old.", "INTEGER")
            else:
                fields.add(field_name, f"{preffix}male population over {age[a]} years old.", "INTEGER")

            project.conn.executemany(f"UPDATE zones SET {field_name}=? WHERE zone_id=?;", list_of_tuples)
            project.conn.commit()

            project.conn.execute(f"UPDATE zones SET {field_name}=0 WHERE {field_name} IS NULL;")
            project.conn.commit()
