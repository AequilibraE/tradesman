import unittest
from os.path import join
from uuid import uuid4
from tempfile import gettempdir

from create_nauru_test import create_nauru_test
from tradesman.model_creation.pop_by_sex_and_age import get_pop_by_sex_age


class TestPopBySexAndAge(unittest.TestCase):
    def setUp(self) -> None:
        self.model_place = "nauru"
        self.fldr = join(gettempdir(), uuid4().hex)
        self.project = create_nauru_test(self.fldr)

    def test_get_pop_by_sex_age(self):
        get_pop_by_sex_age(self.project, self.model_place)

        f_10_pop = self.project.conn.execute("SELECT SUM(POPF10) FROM zones;").fetchone()[0]
        self.assertGreater(f_10_pop, 0)

        f_4_pop = self.project.conn.execute("SELECT SUM(POPF4) FROM zones;").fetchone()[0]
        self.assertGreater(f_4_pop, 0)

        m_5_pop = self.project.conn.execute("SELECT SUM(POPM5) FROM zones;").fetchone()[0]
        self.assertGreater(m_5_pop, 0)

        m_7_pop = self.project.conn.execute("SELECT SUM(POPM7) FROM zones;").fetchone()[0]
        self.assertGreater(m_7_pop, 0)


if __name__ == "__name__":
    unittest.main()
