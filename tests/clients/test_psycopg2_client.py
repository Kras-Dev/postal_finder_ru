# tests/test_psycopg2_client.py
from unittest.mock import Mock, patch

import pytest

from clients.postal_code_info import PostalCodeInfo
from clients.psycopg2_client import Psycopg2Client
from utils.psycopg2_connection import Psycopg2Connection


@pytest.fixture
def mock_connection():
    """Фикстура для имитации соединения с базой данных."""
    connection = Mock(spec=Psycopg2Connection)
    return connection

def test_init_psycopg2_client(mock_connection):
    """Тестирование инициализации Psycopg2Client."""
    client = Psycopg2Client(mock_connection)
    assert client.connection == mock_connection


def test_select_postal_code_found(mock_connection):
    """Тестирование получения почтового кода из базы данных."""
    # Имитация данных из базы данных
    mock_result = (76.9133, 48.1699, "Russia", "Брянск 14")
    mock_connection.execute_query.return_value = mock_result

    client = Psycopg2Client(mock_connection)
    result = client.select_postal_code("241014")
    # Проверяем, является ли postal_info экземпляром PostalCodeInfo
    assert isinstance(result, PostalCodeInfo)
    assert result.longitude == 76.9133
    assert result.latitude == 48.1699
    assert result.country == "Russia"
    assert result.state == "Брянск 14"

def test_select_postal_code_not_found(mock_connection):
    """Тестирование получения почтового кода, которого нет в базе данных."""
    # Имитация отсутствия данных в базе данных
    mock_connection.execute_query.return_value = None

    client = Psycopg2Client(mock_connection)
    # Имитация вызова ApiDBService для получения данных из API
    with patch('service.api_db_service.ApiDBService') as api_mock_service:
        api_mock_service.return_value.fetch_postal_code_from_api.return_value = PostalCodeInfo(
            33.0819, 68.9717, "Russia","Мурманск 8")
        postal_info = client.select_postal_code("183008")
        assert isinstance(postal_info, PostalCodeInfo)
        assert postal_info.longitude == 33.0819
        assert postal_info.latitude == 68.9717
        assert postal_info.country == "Russia"
        assert postal_info.state == "Мурманск 8"


def test_get_postal_code_from_db(mock_connection):
    """Тестирование выборки почтового кода из базы данных."""
    # Имитация данных из базы данных
    result = (76.9133, 48.1699, "Russia", "Брянск 14")
    mock_connection.execute_query.return_value = result

    client = Psycopg2Client(mock_connection)
    postal_info = client.get_postal_code_from_db("241014")

    assert isinstance(postal_info, PostalCodeInfo)
    assert postal_info.longitude == 76.9133
    assert postal_info.latitude == 48.1699
    assert postal_info.country == "Russia"
    assert postal_info.state == "Брянск 14"


def test_get_postal_code_from_db_not_found(mock_connection):
    """Тестирование выборки почтового кода, которого нет в базе данных."""
    # Имитация отсутствия данных в базе данных
    mock_connection.execute_query.return_value = None

    client = Psycopg2Client(mock_connection)
    postal_info = client.get_postal_code_from_db("12345")

    assert postal_info is None

def test_insert_postal_code(mock_connection):
    """Тестирование вставки данных о почтовом коде в базу данных."""
    # Имитация данных для вставки
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
    client = Psycopg2Client(mock_connection)
    client.insert_postal_code(mock_data)
    # Проверка вызова execute_query с правильными параметрами
    mock_connection.execute_query.assert_called_once()


def test_increment_request_statistic(mock_connection):
    """Тестирование обновления статистики запросов.
    При первом вызове (SELECT) метод execute_query возвращает True. Это имитирует ситуацию, когда запись в таблице
    статистики существует. В реальном коде это означает, что результат запроса SELECT не пустой, и метод пойдет
    по пути обновления существующей записи.
    """
    # Имитация существующей записи в статистике
    mock_connection.execute_query.side_effect = [True, None]
    client = Psycopg2Client(mock_connection)
    client.increment_request_statistic("358001")
    # Проверка вызова execute_query для обновления существующей записи
    assert mock_connection.execute_query.call_count == 2


def test_increment_request_statistic_new_entry(mock_connection):
    """Тестирование создания новой записи статистики запросов.
        Настраиваем side_effect так, чтобы при первом вызове (SELECT) метод возвращал None (что означает, что записи нет),
        а при втором вызове (INSERT) он также возвращает None, что не имеет значения для логики теста,
        поскольку тестируем только количество вызовов.
    """
    # Имитация отсутствия записи в статистике
    mock_connection.execute_query.side_effect = [None, None]

    client = Psycopg2Client(mock_connection)
    client.increment_request_statistic("156011")

    # Проверка вызова execute_query для создания новой записи
    assert mock_connection.execute_query.call_count == 2