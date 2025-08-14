import geopandas as gpd
import pandas as pd
from os.path import dirname, isfile, join
from aequilibrae import Project
from scipy.sparse import coo_matrix

from tradesman.utils.mask_raster import mask_raster

from urllib.request import urlretrieve
from tempfile import gettempdir

import numpy as np
from tradesman.utils.tqdm_download import TqdmUpTo


class ImportPopulation:
    def __init__(self, project: Project, source: str = "WorldPop", overwrite: bool = False):
        self.project = project
        self.source = source.lower()
        self.overwrite = overwrite

    def get_file_url(self):
        if self.source not in ["worldpop", "meta"]:
            raise ValueError(f"Population source {self.source} is not available. Try one of 'WorldPop' or 'Meta'.")

        country_code = self.project.about.country_code_three_digit

        if self.source == "worldpop":
            url = "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/{}/{}_ppp_2020.tif"
            return url.format(country_code, country_code.lower())
        else:
            url = pd.read_csv(join(dirname(__file__), "population/all_raster_pop_source.csv"))
            url = url[url.iso_country == country_code]

            if url.empty:
                raise ValueError()

            return url.meta_link.tolist()[0]

    def population_raster(self, data_link: str, field_name: str):
        """
        Reads the population raster.

        Parameters:
            *data_link*(:obj:`str`): URL link to download the file
            *field_name*(:obj:`str`): desired filed name
            *project*(:obj:`aequilibrae.project`): currently open project
        """
        dest_path = join(gettempdir(), f"{field_name}.tif")
        if not isfile(dest_path):
            with TqdmUpTo(unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=f"{field_name}.tif") as t:
                _, _ = urlretrieve(data_link, filename=dest_path, reporthook=t.update_to, data=None)
                t.total = t.n
        model_area = self.get_model_area(True)

        dataset = mask_raster(dest_path, model_area)

        minx, miny, maxx, maxy = model_area.bounds
        width = dataset.width
        height = dataset.height
        x_min = dataset.bounds.left
        y_max = dataset.bounds.top
        x_size, y_size = dataset.res

        # Computes the X and Y indices for the XY grid that will represent our raster
        y_idx = []
        for row in range(height):
            y = row * (-y_size) + y_max + (y_size / 2)  # to centre the point
            y_idx.append(y)
        y_idx = np.array(y_idx)

        x_idx = []
        for col in range(width):
            x = col * x_size + x_min + (x_size / 2)  # add half the cell size
            x_idx.append(x)
        x_idx = np.array(x_idx)

        # Read the data and build the population dataset
        data = dataset.read(1)
        mat = coo_matrix(data)
        rows = y_idx[mat.row]
        cols = x_idx[mat.col]
        df = pd.DataFrame({"longitude": cols, "latitude": rows, "population": mat.data})
        df = df.loc[df.population >= 0, :]  # Pixels outside the modeled area have negative values
        df = df[(df.longitude > minx) & (df.longitude < maxx) & (df.latitude > miny) & (df.latitude < maxy)]
        df.fillna(0, inplace=True)

        return df

    def get_model_area(self, is_polygon: bool = False):
        with self.project.db_connection as conn:
            model_area = gpd.read_postgis(
                "SELECT ST_AsBinary(geometry) as geom FROM political_subdivisions WHERE level=-1",
                con=conn,
                crs="EPSG:4326",
            )
            if is_polygon:
                return model_area.geom[0]
            return model_area

    def get_overall_population(self):
        url = self.get_file_url()
        df = self.population_raster(url, f"pop_{self.project.country_name}")
        population = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326)

        model_area = self.get_model_area()
        population = population.clip(model_area, keep_geom_type=True)[["longitude", "latitude", "population"]]

        with self.project.db_connection as conn:
            population.to_sql("raw_population", conn, if_exists="append", index=False)
            conn.execute("UPDATE raw_population SET Geometry=MakePoint(longitude, latitude, 4326)")

    def get_stratified_population(self):
        """
        Imports population by sex and age into the model.

        Parameters:
            *project*(:obj:`aequilibrae.project`): currently open project
            *country_name*(:obj:`str`): model place country
        """
        url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2000_2020/2020/{}/{}_{}_{}_2020.tif"
        sex = ["f", "m"]
        age = [0, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
        country_code = self.project.about.country_code_three_digit

        zoning = self.project.zoning
        fields = zoning.fields

        zones = zoning.data

        for s in sex:
            for idx, a in enumerate(age):
                data_link = url.format(country_code, country_code.lower(), s, a)
                field_name = f"POP{s.upper()}{a}"

                df = self.population_raster(data_link, field_name=f"{country_code}_{field_name}")

                population = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326)
                population = zones.sjoin(population).groupby("zone_id").sum(numeric_only=True).astype(int)
                population.reset_index(inplace=True)

                list_of_tuples = list(population[["population", "zone_id"]].itertuples(False, None))

                preffix = "" if s == "m" else "fe"
                if a < 80:
                    fields.add(field_name, f"{preffix}male population {a} to {age[idx+1]} years old.", "INTEGER")
                else:
                    fields.add(field_name, f"{preffix}male population over {a} years old.", "INTEGER")

                with self.project.db_connection as conn:
                    conn.executemany(f"UPDATE zones SET {field_name}=? WHERE zone_id=?;", list_of_tuples)
                    conn.execute(f"UPDATE zones SET {field_name}=0 WHERE {field_name} IS NULL;")
