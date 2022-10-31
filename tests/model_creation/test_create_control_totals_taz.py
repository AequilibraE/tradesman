import unittest
from os import rename
from os.path import exists, join
from shutil import rmtree
from tempfile import gettempdir, mkdtemp
from uuid import uuid4

from tests.create_nauru_test import create_nauru_test
from tradesman.model_creation.pop_by_sex_and_age import get_pop_by_sex_age
from tradesman.model_creation.synthetic_population.create_control_totals_taz import create_control_totals_taz


class TestCreateTotalsTaz(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = mkdtemp()
        # rmtree(join(gettempdir(), "data"))
        self.fldr = join(gettempdir(), "data")
        rename(temp_fldr, self.fldr)
        self.prj_fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.prj_fldr)
        self.model_place = "Nauru"
        get_pop_by_sex_age(self.project, self.model_place)

    def tearDown(self) -> None:
        rmtree(join(gettempdir(), "data"))

    def test_create_control_totals_taz(self):
        create_control_totals_taz(self.project, self.model_place, gettempdir())

        self.assertTrue(exists(join(gettempdir(), "data/control_totals_taz.csv")))


if __name__ == "__name__":
    unittest.main()
