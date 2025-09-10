import pandas as pd
import pytest

from tradesman.model_creation.import_population import ImportPopulation


def test_exception(nauru_no_pop):
    with pytest.raises(ValueError):
        population = ImportPopulation(nauru_no_pop, source="TraDesMaN")
        population.get_file_url()


@pytest.mark.parametrize("source", ["Meta", "WorldPop"])
def test_import_population(source: str, nauru_no_pop, mocker):
    mock = pd.DataFrame(
        [[166.92607, -0.53451, 5.045551], [166.92357, -0.54684, 3.902642]],
        columns=["longitude", "latitude", "population"],
    )

    file_func = "tradesman.model_creation.import_population.ImportPopulation.population_raster"
    mocker.patch(file_func, return_value=mock)

    population = ImportPopulation(nauru_no_pop, source)
    population.get_overall_population()

    with nauru_no_pop.db_connection as conn:
        assert conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0] > 8
