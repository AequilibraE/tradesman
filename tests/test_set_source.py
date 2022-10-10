import unittest

from tradesman.model_creation.set_source import set_source


class TestSetSource(unittest.TestCase):
    @unittest.skip
    def test_set_source(self):
        self.assertEqual(set_source("MetA"), "Meta")
        self.assertEqual(set_source("WORLDPOP"), "WorldPop")

    @unittest.skip
    def test_set_source_exception(self):
        with self.assertRaises(ValueError) as exception_context:
            set_source("worlddata")
        self.assertEqual(str(exception_context.exception), "No population source found.")


if __name__ == "__name__":
    unittest.main()
