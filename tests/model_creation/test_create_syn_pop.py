from tempfile import gettempdir
import unittest
from os.path import join, exists, abspath, dirname
from uuid import uuid4
import yaml
import pandas as pd
from create_nauru_test import create_nauru_test
from tradesman.model_creation.pop_by_sex_and_age import get_pop_by_sex_age
from tradesman.model_creation.synthetic_population.create_control_totals_meta import create_control_totals_meta
from tradesman.model_creation.synthetic_population.create_control_totals_taz import create_control_totals_taz
from tradesman.model_creation.synthetic_population.create_geo_crosswalk import create_geo_cross_walk
from tradesman.model_creation.synthetic_population.create_seeds import create_buckets
from tradesman.model_creation.synthetic_population.create_syn_pop import set_thread_number
from tradesman.model_creation.synthetic_population.unzip_files import unzip_control_and_seed_files


class TestCreateSynPop(unittest.TestCase):
    def setUp(self) -> None:
        self.model_place = "nauru"
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)
        self.pop_fldr = join(self.fldr, "nauru/population")

    @unittest.skip
    def test_create_control_total_taz(self):
        """
        O teste passa se o arquivo existir na pasta population/data
        """
        create_control_totals_taz(self.project, self.model_place, self.pop_fldr)

        self.assertTrue(exists(join(self.pop_fldr, "data/control_totals_taz.csv")))


if __name__ == "__name__":
    unittest.main()
