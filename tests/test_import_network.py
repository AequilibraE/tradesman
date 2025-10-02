import pytest
from os import environ
from os.path import join, abspath, dirname

from tradesman.model_creation.import_network import ImportNetwork


@pytest.mark.skipif(bool(environ.get("CI")), reason="Does not run in GitHub Action")
def test_import_from_gmns(empty_aequilibrae_model):
    fields = ["model_place", "address_type", "country_name", "country_code_two_digit", "country_code_three_digit"]
    fields.extend(["xmin", "ymin", "xmax", "ymax"])

    about = empty_aequilibrae_model.about
    for field in fields:
        about.add_info_field(field)

    about.model_place = "Monaco"
    about.address_type = "country"
    about.country_name = "Monaco"
    about.country_code_two_digit = "MC"
    about.country_code_three_digit = "MCO"
    about.xmin = 7.4064
    about.ymin = 43.7253
    about.xmax = 7.4392
    about.ymax = 43.7517

    pbf_path = join(abspath(dirname("tests")), "tests/data/monaco/monaco-latest.osm.pbf")

    network = ImportNetwork(empty_aequilibrae_model, pbf_path=pbf_path)
    network.build_network()

    links = empty_aequilibrae_model.network.links.data

    assert links.shape[0] > 0
    for i in ["bridge", "toll", "tunnel"]:
        assert i in links.columns


@pytest.mark.skipif(bool(environ.get("CI")), reason="Does not run in GitHub Action")
def test_import_from_osm(empty_aequilibrae_model):
    about = empty_aequilibrae_model.about
    about.add_info_field("model_place")

    about.model_place = "Monaco"

    network = ImportNetwork(empty_aequilibrae_model)
    network.build_network()

    links = empty_aequilibrae_model.network.links.data

    assert links.shape[0] > 0
    for i in ["bridge", "toll", "tunnel"]:
        assert i in links.columns
