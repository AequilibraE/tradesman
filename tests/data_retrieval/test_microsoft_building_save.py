import numpy as np
import pandas as pd
import geopandas as gpd
from tempfile import gettempdir
from os.path import join
import unittest
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test
from tests.data.nauru.points_in_nauru import list_of_wkb
from tradesman.data_retrieval.osm_tags.microsoft_buildings_save import save_microsoft_buildings


class TestSaveMicrosoftBuildings(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)
        self.df = pd.DataFrame(np.ones(shape=(10, 3)), columns=["id", "area", "zone_id"])
        self.df.insert(3, "geom_wkb", list_of_wkb)
        self.gdf = gpd.GeoDataFrame(self.df, geometry=gpd.GeoSeries.from_wkb(self.df.geom_wkb), crs=4326)

    def test_save_microsoft_buildings(self):

        save_microsoft_buildings(self.gdf, self.project)

        self.assertEqual(self.project.conn.execute("SELECT SUM(microsoft_building_area) FROM zones;").fetchone()[0], 10)

        self.assertEqual(
            self.project.conn.execute("SELECT COUNT(microsoft_building_count) FROM zones;").fetchone()[0], 19
        )


if __name__ == "__name__":
    unittest.main()
