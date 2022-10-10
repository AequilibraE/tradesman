from shutil import rmtree
import tempfile
import unittest
import yaml
from os.path import join
from os import rename
from tempfile import gettempdir
import multiprocessing as mp

from tradesman.model_creation.synthetic_population.create_synthetic_population import update_thread_number

LAYOUT = """num_processes: 1
multiprocess_steps:
- begin: input_pre_processor
- num_processes: 1
"""


def get_layout_from_path(path):
    with open(path, "r") as f:
        return yaml.full_load(f)


class TestSetThreadNumber(unittest.TestCase):
    def setUp(self) -> None:
        temp_fldr = tempfile.mkdtemp()
        self.fldr = join(gettempdir(), "configs")
        rename(temp_fldr, self.fldr)

        with open(join(self.fldr, "settings.yaml"), mode="w") as file:
            file.write("num_processes: 1")

        mp_temp = tempfile.mkdtemp()
        self.mp_fldr = join(gettempdir(), "configs_mp")
        rename(mp_temp, self.mp_fldr)

        with open(join(self.mp_fldr, "settings.yaml"), mode="w") as mp_file:
            mp_file.write(LAYOUT)

    def tearDown(self) -> None:
        rmtree(join(tempfile.gettempdir(), "configs"))
        rmtree(join(tempfile.gettempdir(), "configs_mp"))

    @unittest.skip
    def test_set_thread_number_integer(self):

        update_thread_number(gettempdir(), number=2)

        doc = get_layout_from_path(join(self.mp_fldr, "settings.yaml"))

        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": 2})
        self.assertEqual(doc["num_processes"], 2)
        self.assertEqual(doc["multiprocess_steps"][1]["num_processes"], 2)

    @unittest.skip
    def test_set_thread_number_float(self):
        doc = get_layout_from_path(join(self.mp_fldr, "settings.yaml"))

        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": 2})
        self.assertEqual(doc["num_processes"], 2)
        self.assertEqual(doc["multiprocess_steps"][1]["num_processes"], 2)

    @unittest.skip
    def test_set_thread_number_greater(self):

        num = mp.cpu_count() + 2
        update_thread_number(gettempdir(), number=num)
        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": mp.cpu_count()})

    # @unittest.skip
    # def test_set_thread_number_none(self):

    #     doc = get_layout_from_path(join(self.mp_fldr, "settings.yaml"))

    #     set_thread_number(gettempdir(), number=None)
    #     self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": mp.cpu_count()})
    #     self.assertEqual(doc["num_processes"], mp.cpu_count())
    #     self.assertEqual(doc["multiprocess_steps"][1]["num_processes"], mp.cpu_count())

    @unittest.skip
    def test_set_thread_number_zero(self):
        doc = get_layout_from_path(join(self.mp_fldr, "settings.yaml"))

        self.assertEqual(get_layout_from_path(join(self.fldr, "settings.yaml")), {"num_processes": mp.cpu_count()})
        self.assertEqual(doc["num_processes"], mp.cpu_count())
        self.assertEqual(doc["multiprocess_steps"][1]["num_processes"], mp.cpu_count())


if __name__ == "__name__":
    unittest.main()
