import unittest

from tradesman.data.population_file_address import link_source


class TestPopulationFileAddress(unittest.TestCase):
    def test_link_source_world_pop(self):
        self.assertEqual(
            link_source(country_name="Nauru", source="WorldPop"),
            "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/NRU/nru_ppp_2020.tif",
        )

    def test_link_source_meta_with_file(self):
        self.assertEqual(
            link_source(country_name="Nauru", source="Meta"),
            "https://data.humdata.org/dataset/ecb31702-827b-4a93-bd6e-149753df2349/resource/03cd9363-13eb-422c-bf72-4bc3504b6288/download/population_nru_2018-10-01_geotiff.zip",
        )

    def test_link_source_meta_no_file(self):
        self.assertEqual(link_source(country_name="Namibia", source="Meta"), "no file")

    def test_link_source_exception(self):
        with self.assertRaises(ValueError) as exception_context:
            link_source(country_name="Nauru", source="OurLand")

        self.assertEqual(str(exception_context.exception), "No population source found.")


if __name__ == "__name__":
    unittest.main()
