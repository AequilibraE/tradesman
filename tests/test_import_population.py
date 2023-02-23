import pytest
import pandas as pd

from tradesman.model_creation.import_population import import_population


def test_exception(nauru_test):
    with pytest.raises(ValueError):
        import_population(project=nauru_test, country_name="Namibia", source="Meta", overwrite=False)


class MockResponse:
    @staticmethod
    def population_raster():
        return pd.DataFrame(
            [[166.92607, -0.53451, 5.045551], [166.92357, -0.54684, 3.902642]],
            columns=["longitude", "latitude", "population"],
        )


@pytest.fixture
def mock_raster(monkeypatch):
    def mock_return(*args, **kwargs):
        return MockResponse.population_raster()

    monkeypatch.setattr("tradesman.model_creation.import_population.population_raster", mock_return)


@pytest.mark.parametrize("source", ["Meta", "WorldPop"])
def test_import_population(source: str, nauru_test, mock_raster):
    import_population(project=nauru_test, country_name="Nauru", source=source, overwrite=True)

    assert nauru_test.conn.execute("SELECT SUM(population) FROM raw_population;").fetchone()[0] > 8
