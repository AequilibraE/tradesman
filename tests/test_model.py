import unittest
import uuid

from os.path import join

from tempfile import gettempdir

from unittest import TestCase

from tradesman.model import Tradesman

# from tradesman.model_creation.create_new_tables import add_new_tables


class TestModel(TestCase):
    def setUp(self) -> None:
        dir = join(gettempdir(), uuid.uuid4().hex)
        # dir = join(gettempdir(), "ANDORRA")
        self.proj = Tradesman(dir, "Nauru")
        # add_new_tables(self.proj.conn)

    @unittest.skip
    def test_create(self):
        self.proj.create()

    # def test_set_population_source(self):
    #     self.fail()

    # def test_import_network(self):
    #     self.proj.import_network()

    # def test_import_subdivisions(self):
    #     self.fail()
    #
    # def test_import_population(self):
    #     self.fail()
    #
    # def test_build_zoning(self):
    #     self.proj.build_zoning(overwrite=True)
    #

    # def test_place(self):
    #     self.fail()
