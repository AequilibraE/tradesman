import unittest
import pandas as pd
from tradesman.data_retrieval.osm_tags.import_osm_data import point_or_polygon


class TestPointOrPolygon(unittest.TestCase):
    # @unittest.skip
    def test_point_or_polygon_return_point(self):
        df = pd.DataFrame([[0, "node", 0, 1, None]], columns=["id", "type", "lat", "lon", "geometry"])

        for _, row in df.iterrows():
            x = point_or_polygon(row)

        self.assertEqual(x, b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00")

    def test_point_to_polygon_return_polygon(self):
        df = pd.DataFrame(
            [
                [
                    0,
                    "reference",
                    None,
                    None,
                    [
                        {"lat": 0, "lon": 0},
                        {"lat": 0, "lon": 1},
                        {"lat": 1, "lon": 1},
                        {"lat": 1, "lon": 0},
                        {"lat": 0, "lon": 0},
                    ],
                ]
            ],
            columns=["id", "type", "lat", "lon", "geometry"],
        )

        for _, row in df.iterrows():
            x = point_or_polygon(row)

        self.assertEqual(
            x,
            b"\x01\x03\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )


if __name__ == "__name__":
    unittest.main()
