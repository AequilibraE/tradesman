import unittest

from tradesman.model_creation.set_source import set_political_boundaries_source, set_population_source


class TestSetSource(unittest.TestCase):
    def test_set_population_source(self):
        self.assertEqual(set_population_source("MetA"), "Meta")
        self.assertEqual(set_population_source("WORLDPOP"), "WorldPop")

    def test_set_population_source_exception(self):
        with self.assertRaises(ValueError) as exception_context:
            set_population_source("worlddata")
        self.assertEqual(str(exception_context.exception), "No population source found.")

    def test_set_boundaries_source(self):
        self.assertEqual(set_political_boundaries_source("GAdm"), "GADM")
        self.assertEqual(set_political_boundaries_source("GEOBoundaries"), "GeoBoundaries")

    def test_set_boundaries_source_exception(self):
        with self.assertRaises(ValueError) as exception_context:
            set_political_boundaries_source("dinosaur")
        self.assertEqual(str(exception_context.exception), "Source not available.")


if __name__ == "__name__":
    unittest.main()
