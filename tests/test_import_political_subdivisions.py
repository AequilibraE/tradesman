import pytest
from tradesman.model import Tradesman
from tradesman.model_creation.import_political_subdivisions import ImportPoliticalSubdivisions


def test_import_model_exception(create_path):
    model = Tradesman(network_path=create_path, model_place="Charlie and the chocolate factory")

    with pytest.raises(ValueError):
        model.import_model_area()


def test_unexistent_source(create_path):
    with pytest.raises(ValueError):
        Tradesman(network_path=create_path, model_place="Coquimbo, Chile", boundaries_source="Cencosud")


@pytest.mark.parametrize("source", ["GADM", "geoBoundaries"])
def test_add_subdivisions(source: str, empty_aequilibrae_model, network_connection):
    model = ImportPoliticalSubdivisions(model_place="Coquimbo, Chile", source=source, project=empty_aequilibrae_model)

    model.import_model_area()
    assert network_connection.execute("SELECT COUNT(*) FROM political_subdivisions WHERE level=-1;").fetchone()[0], 1

    model.add_country_borders(False)
    assert network_connection.execute("SELECT COUNT(*) FROM political_subdivisions WHERE level=0;").fetchone()[0], 1

    model.import_subdivisions(2, False)
    assert network_connection.execute("SELECT COUNT(*) FROM political_subdivisions WHERE level>0;").fetchone()[0] >= 4

    assert network_connection.execute("SELECT COUNT(*) FROM political_subdivisions;").fetchone()[0] >= 5
