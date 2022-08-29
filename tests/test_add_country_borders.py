import uuid
from os.path import join
from tempfile import gettempdir
from unittest import TestCase

from tests.create_nauru_test import create_nauru_test
from tradesman.model_creation.add_country_borders import get_borders_online


class TestCountryBorders(TestCase):
    def setUp(self) -> None:
        self.fldr = join(gettempdir(), uuid.uuid4().hex)
        create_nauru_test(self.fldr)

    def test_add_borders(self):
        geo = get_borders_online("Armenia", 1)
        self.assertGreater(geo.area, 3)
        self.assertLess(geo.area, 4)
