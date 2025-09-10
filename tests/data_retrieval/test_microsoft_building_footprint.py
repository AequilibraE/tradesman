from unittest.mock import Mock, patch

import pandas as pd
import pytest

from tests.create_nauru_test import create_nauru_test
from tradesman.data_retrieval.microsoft_building_data import ImportMicrosoftBuildingData

CSV_DATA = """Location,QuadKey,Url,Size,UploadDate
Monaco,120223030,https://minedbuildings.z5.web.core.windows.net/global-buildings/2025-02-25/global-buildings.geojsonl/RegionName=Monaco/quadkey=120223030/part-00016-5cf70943-9c5f-4fc6-94fb-43ce5feefa56.c000.csv.gz,148.0KB,2025-02-28
"""


@pytest.fixture
def mock_url_response():
    """Fixture que retorna mock response com CSV"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = CSV_DATA
    mock_response.json.side_effect = ValueError("No JSON object could be decoded")
    return mock_response


def test_microsoft_buildings_no_bld(create_path, mock_url_response):
    project = create_nauru_test(create_path)

    buildings = ImportMicrosoftBuildingData(project)
    with patch("tradesman.data_retrieval.microsoft_building_data.requests.get", return_value=mock_url_response):
        buildings.get_buildings()


def test_microsoft_buildings_with_bld(empty_aequilibrae_model, mock_url_response):
    # We add model information to the project
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
    about.xmin = 7.4037113
    about.ymin = 43.7196129
    about.xmax = 7.4876594
    about.ymax = 43.7574357

    # Import data
    buildings = ImportMicrosoftBuildingData(empty_aequilibrae_model)
    with patch("tradesman.data_retrieval.microsoft_building_data.requests.get", return_value=mock_url_response):
        buildings.get_buildings()

    with empty_aequilibrae_model.db_connection as conn:
        df = pd.read_sql("SELECT mcr_bld_count, mcr_bld_area FROM zones;", con=conn)

    assert "mcr_bld_count" in df.columns.values
    assert "mcr_bld_area" in df.columns.values
