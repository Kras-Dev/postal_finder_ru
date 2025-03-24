# tests/service/test_api_db_service.py
from unittest.mock import Mock, patch

import pytest

from clients.api_client import ApiClient
from clients.postal_code_info import PostalCodeInfo
from clients.sqlalchemy_client import SqlAlchemyClient
from service.api_db_service import ApiDBService


@pytest.fixture
def mock_db_client():
    """Фикстура для имитации клиента базы данных."""
    return Mock(spec=SqlAlchemyClient)

@pytest.fixture
def mock_api_client():
    """Фикстура для имитации клиента API."""
    return Mock(spec=ApiClient)

class TestApiDBService:
    """Класс для тестирования SQLAlchemyClient."""
    def test_init_api_db_service(self, mock_db_client):
        """Тестирование инициализации ApiDBService."""
        service = ApiDBService(mock_db_client)
        assert service.db_client == mock_db_client

    def test_fetch_postal_code_from_api_found(self,mock_db_client, mock_api_client):
        """Тестирование получения данных о почтовом коде из API и их сохранения в базе данных."""
        mock_data = {
            'post code': '241014',
            'country': 'Russia',
            'country abbreviation': 'RU',
            'places': [
                {
                    'place name': 'Брянск',
                    'longitude': 76.9133,
                    'latitude': 48.1699,
                    'state': 'Брянск 14',
                    'state abbreviation': ''
                }
            ]
        }
        """ Настройка мока для ApiClient """
        with patch('clients.api_client.ApiClient', return_value=mock_api_client):
            mock_api_client.get_postal_data.return_value = mock_data
            service = ApiDBService(mock_db_client)
            result = service.fetch_postal_code_from_api("241014")
            assert isinstance(result, PostalCodeInfo)
            assert result.longitude == 76.9133
            assert result.latitude == 48.1699
            assert result.country == "Russia"
            assert result.state == "Брянск 14"

            mock_db_client.insert_postal_code.assert_called_once()
            mock_db_client.increment_request_statistic.assert_called_once()


    def test_fetch_postal_code_from_api_not_found(self,mock_db_client, mock_api_client):
        """Тестирование получения данных о почтовом коде из API, когда данные не найдены."""
        """ Настройка мока для ApiClient """
        with patch('clients.api_client.ApiClient', return_value=mock_api_client):
            mock_api_client.get_postal_data.return_value = None

            service = ApiDBService(mock_db_client)
            result = service.fetch_postal_code_from_api("241014")
            assert result is None
            mock_db_client.insert_postal_code.assert_not_called()
            mock_db_client.increment_request_statistic.assert_not_called()