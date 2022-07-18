import uuid

from os.path import join

from tempfile import gettempdir

from unittest import TestCase

from tradesman.model import Tradesman


class TestModel(TestCase):

    def setUp(self) -> None:
        dir = join(gettempdir(), uuid.uuid4().hex)

        self.proj = Tradesman(dir, "Andorra")

    #

    # def test_create(self):
    #     self.fail()
    #

    # def test_set_population_source(self):
    #     self.fail()

    def test_import_network(self):
        self.proj.import_network()

    # def test_import_subdivisions(self):
    #     self.fail()
    #
    # def test_import_population(self):
    #     self.fail()
    #

    # def test_build_zoning(self):
    #     self.fail()
    #

    # def test_place(self):
    #     self.fail()
