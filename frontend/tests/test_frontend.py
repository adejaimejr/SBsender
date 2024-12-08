import pytest
import requests

BASE_URL = "http://localhost:8501"

@pytest.mark.skip(reason="Streamlit tests require running server")
def test_dashboard_access():
    response = requests.get(BASE_URL)
    assert response.status_code == 200
