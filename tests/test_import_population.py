import pytest
import pandas as pd

from tradesman.model_creation.import_population import ImportPopulation


def test_exception(nauru_test):
    with pytest.raises(ValueError):
        population = ImportPopulation(nauru_test, source="TraDesMaN")
        population.get_file_url()


@pytest.mark.parametrize("source", ["Meta", "WorldPop"])
def test_import_population(source: str, nauru_test, mocker):
    mock = pd.DataFrame(
        [[166.92607, -0.53451, 5.045551], [166.92357, -0.54684, 3.902642]],
        columns=["longitude", "latitude", "population"],
    )

    file_func = "tradesman.model_creation.import_population.ImportPopulation.population_raster"
    mocker.patch(file_func, return_value=mock)

    population = ImportPopulation(nauru_test, source)
    population.get_overall_population()

    with nauru_test.db_connection as conn:
        assert conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0] > 8
