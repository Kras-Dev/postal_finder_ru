# tests/test_sqlalchemy_client.py
from unittest.mock import Mock, MagicMock, patch

import pytest

from clients.postal_code_info import PostalCodeInfo
from clients.sqlalchemy_client import SqlAlchemyClient
from models.sqlalchemy_models import PostalCodeRequestStatistics
from utils.sqlalchemy_connection import SQLAlchemyConnection

@pytest.fixture
def mock_session():
    """Фикстура для имитации сессии SQLAlchemy."""
    session = MagicMock()
    """ Устанавливаем поведение для контекстного менеджера (with session as s):
        Когда сессия используется как контекстный менеджер, она должна возвращать саму себя"""
    session.__enter__.return_value = session
    """ Устанавливаем поведение для выхода из контекстного менеджера (после блоков with)"""
    session.__exit__.return_value = None
    session.commit = Mock()
    return session

@pytest.fixture
def mock_connection(mock_session):
    """Фикстура для имитации соединения SQLAlchemy."""
    connection = Mock(spec=SQLAlchemyConnection)
    connection.get_session.return_value = mock_session
    return connection

class TestSQLAlchemyClient:
    """Класс для тестирования ApiDBService."""
    def test_init_sqlalchemy_client(self, mock_connection):
        """Тестирование инициализации SqlAlchemyClient."""
        client =SqlAlchemyClient(mock_connection)
        assert client.connection == mock_connection

    def test_select_postal_code_found(self, mock_connection, mock_session):
        """Тестирование получения почтового кода из базы данных."""
        client = SqlAlchemyClient(mock_connection)
        """ Настраиваем мок для возврата данных """
        mock_result = (76.9133, 48.1699, "Russia", "Брянск 14")
        """ Настройка мока для возврата объекта с данными о почтовом коде """
        mock_session.execute.return_value.fetchone.return_value = mock_result
        result = client.get_postal_code_from_db("241014")
        assert isinstance(result, PostalCodeInfo)
        assert result.longitude == 76.9133
        assert result.latitude == 48.1699
        assert result.country == "Russia"
        assert result.state == "Брянск 14"
        mock_session.commit.assert_called_once()

    def test_select_postal_code_not_found(self, mock_connection, mock_session):
        """Тестирование получения почтового кода, которого нет в базе данных."""
        client = SqlAlchemyClient(mock_connection)
        mock_session.execute.return_value.fetchone.return_value = None
        with patch('service.api_db_service.ApiDBService') as api_mock_service:
            api_mock_service.return_value.fetch_postal_code_from_api.return_value = PostalCodeInfo(
                33.0819, 68.9717, "Russia","Мурманск 8")
            result = client.select_postal_code("183008")
            assert isinstance(result, PostalCodeInfo)
            assert result.longitude == 33.0819
            assert result.latitude == 68.9717
            assert result.country == "Russia"
            assert result.state == "Мурманск 8"

    def test_get_postal_code_from_db(self, mock_connection, mock_session):
        """Тестирование выборки почтового кода из базы данных."""
        """ Имитация данных из базы данных """
        mock_result = (76.9133, 48.1699, "Russia", "Брянск 14")
        mock_session.execute.return_value.fetchone.return_value = mock_result
        client = SqlAlchemyClient(mock_connection)
        result = client.get_postal_code_from_db("241014")
        assert isinstance(result, PostalCodeInfo)
        assert result.longitude == 76.9133
        assert result.latitude == 48.1699
        assert result.country == "Russia"
        assert result.state == "Брянск 14"

    def test_get_postal_code_from_db_not_found(self, mock_connection, mock_session):
        """Тестирование выборки почтового кода из базы данных, когда код не найден."""
        client = SqlAlchemyClient(mock_connection)
        mock_session.execute.return_value.fetchone.return_value = None
        result = client.get_postal_code_from_db("241014")
        assert result is None
        mock_session.commit.assert_not_called()

    def test_insert_postal_code(self, mock_connection, mock_session):
        """Тестирование вставки информации о почтовом коде в базу данных."""
        mock_data = {
            "post code": "358001",
            "country": "Russia",
            "country abbreviation": "RU",
            "places": [
                {
                    "place name": "Элиста 1",
                    "longitude": "44.2558",
                    "state": "Калмыкия Республика",
                    "state abbreviation": "",
                    "latitude": "46.3078"
                }
            ]
        }
        client = SqlAlchemyClient(mock_connection)
        client.insert_postal_code(mock_data)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


    def test_increment_request_statistic(self, mock_connection, mock_session):
        """Тестирование обновления статистики запросов для почтового кода. """
        client = SqlAlchemyClient(mock_connection)
        """Случай, когда запись статистики существует"""
        mock_statistic = Mock()
        mock_statistic.request_count = 1
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_statistic

        client.increment_request_statistic("241014")
        assert mock_statistic.request_count == 2
        mock_session.commit.assert_called_once()

        """Сброс вызовов commit для нового тестового сценария"""
        mock_session.commit.reset_mock()

        """Случай, когда записи статистики нет"""
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        client.increment_request_statistic("241015")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
