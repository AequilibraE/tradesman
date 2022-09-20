from os.path import join
from tempfile import gettempdir
from uuid import uuid4
import pandas as pd
import numpy as np
import geopandas as gpd
import unittest

from tests.create_nauru_test import create_nauru_test
from tests.data.nauru.points_in_nauru import list_of_wkb
from tradesman.data_retrieval.osm_tags.osm_buildings_save import save_osm_buildings


class TestOsmBuildingsSave(unittest.TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)
        self.df = pd.DataFrame(np.ones(shape=(10, 3)), columns=["id", "area", "zone_id"])
        self.df.insert(3, "geom_wkb", list_of_wkb)
        self.df.insert(4, "building", list(5 * ["residential"] + 3 * ["cars"] + 2 * ["others"]))
        self.df.insert(0, "type", list(10 * ["testcase"]))
        self.gdf = gpd.GeoDataFrame(self.df, geometry=gpd.GeoSeries.from_wkb(self.df.geom_wkb), crs=4326)

    def tearDown(self) -> None:
        return super().tearDown()

    def test_save_osm_buildings(self):
        save_osm_buildings(self.gdf, self.project)

        self.assertEqual(
            self.project.conn.execute("SELECT SUM(osm_residential_building_area) FROM zones;").fetchone()[0], 5
        )

        self.assertEqual(self.project.conn.execute("SELECT COUNT(osm_cars_building) FROM zones;").fetchone()[0], 1)


if __name__ == "__name__":
    unittest.main()
