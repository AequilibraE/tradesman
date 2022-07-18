from unittest import TestCase

from tradesman.model_creation.add_country_borders import get_borders_online


class TestCountryBorders(TestCase):
    def test_add_borders(self):
        geo = get_borders_online('Armenia', 1)
        self.assertGreater(geo.area, 3)
        self.assertLess(geo.area, 4)
