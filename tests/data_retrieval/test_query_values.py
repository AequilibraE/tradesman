import unittest
import pandas as pd
import numpy as np

from tradesman.data_retrieval.osm_tags.query_writer import amenity_count_query, building_area_query, building_count_query


class TestOsmTagVAlues(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(np.ones(shape=(3, 3)), columns=['transport', "housing", "hospitals"])

    def tearDown(self) -> None:
        return super().tearDown()

    def test_amenity_count_query_kwargs(self):
        self.assertEqual(amenity_count_query(self.df),
                         'UPDATE zones SET osm_transport_amenity=?, osm_housing_amenity=? WHERE zone_id=?;')

    def test_amenity_count_query_no_kwargs(self):
        self.assertEqual(amenity_count_query(self.df, func="set_zero"),
                         'UPDATE zones SET osm_transport_amenity=0, osm_housing_amenity=0 WHERE zone_id=?;')

    def test_building_count_query_kwargs(self):
        self.assertEqual(building_count_query(self.df),
                         'UPDATE zones SET osm_transport_building=?, osm_housing_building=? WHERE zone_id=?;')

    def test_building_count_query_no_kwargs(self):
        self.assertEqual(building_count_query(self.df, func="set_zero"),
                         'UPDATE zones SET osm_transport_building=0, osm_housing_building=0 WHERE zone_id=?;')

    def test_building_area_query_kwargs(self):
        self.assertEqual(building_area_query(self.df),
                         'UPDATE zones SET osm_transport_building_area=ROUND(?,2), osm_housing_building_area=ROUND(?,2) WHERE zone_id=?;')

    def test_building_area_query_no_kwargs(self):
        self.assertEqual(building_area_query(self.df, func="set_zero"),
                         'UPDATE zones SET osm_transport_building_area=0, osm_housing_building_area=0 WHERE zone_id=?;')


if __name__ == "__name__":
    unittest.main()
