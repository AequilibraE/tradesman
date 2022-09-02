from shutil import rmtree
import tempfile
import unittest
import yaml
from os.path import join
from os import rename
from tempfile import gettempdir
import multiprocessing as mp

from tradesman.model_creation.synthetic_population.create_syn_pop import set_thread_number

LAYOUT = "num_processes: 1"


def get_layout_from_path(path):
    with open(path, "r") as f:
        return yaml.full_load(f)


class TestSetThreadNumber(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = tempfile.mkdtemp()
        self.fldr = join(gettempdir(), "configs")
        rename(temp_fldr, self.fldr)

        with open(join(self.fldr, "settings.yaml"), mode="w") as file:
            file.write(LAYOUT)

    def tearDown(self) -> None:
        rmtree(join(tempfile.gettempdir(), "configs"))

    def test_set_thread_number_integer(self):

        set_thread_number(gettempdir(), number=5)

        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": 5})

    def test_set_thread_number_float(self):

        set_thread_number(gettempdir(), number=5.7)

        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": 5})

    def test_set_thread_number_greater(self):

        num = mp.cpu_count() + 2
        set_thread_number(gettempdir(), number=num)

        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": mp.cpu_count()})

    def test_set_thread_number_none(self):

        set_thread_number(gettempdir(), number=None)

        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": mp.cpu_count()})

    def test_set_thread_number_zero(self):

        set_thread_number(gettempdir(), number=0)

        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": mp.cpu_count()})


if __name__ == "__name__":
    unittest.main()
