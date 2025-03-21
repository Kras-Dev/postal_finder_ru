# tests/test_api_client.py
import pytest
import requests
from clients.api_client import ApiClient

@pytest.fixture
def api_client():
    """Фикстура для создания экземпляра ApiClient."""
    return ApiClient()

def test_get_postal_data_success(requests_mock, api_client):
    """Тест успешного получения данных о почтовом индексе."""
    post_code = "241014"
    expected_response = {
        "post code": "241014",
        "country": "Russia",
        "country abbreviation": "RU",
        "places": [
            {
                "place name": "Брянск 14",
                "longitude": "76.9133",
                "state": "Брянская Область",
                "state abbreviation": "",
                "latitude": "48.1699"
            }
        ]
    }
    # Настройка мока для ответа API
    requests_mock.get(f"https://api.zippopotam.us/RU/{post_code}", json=expected_response, status_code=200)
    result = api_client.get_postal_data(post_code)
    assert result == expected_response


def test_get_postal_data_not_found(requests_mock, api_client):
    """Тест обработки ошибки 404 при запросе несуществующего почтового индекса."""
    post_code = "000000"
    # Настройка мока для ответа API с ошибкой 404
    requests_mock.get(f"https://api.zippopotam.us/RU/{post_code}", status_code=404)
    result = api_client.get_postal_data(post_code)
    assert result is None


def test_get_postal_data_request_exception(requests_mock, api_client):
    """Тест обработки исключения запроса."""
    post_code = "500000"
    # Настройка мока для имитации исключения (например, таймаута)
    requests_mock.get(f"https://api.zippopotam.us/RU/{post_code}", exc=requests.exceptions.Timeout)
    result = api_client.get_postal_data(post_code)
    assert result is None
