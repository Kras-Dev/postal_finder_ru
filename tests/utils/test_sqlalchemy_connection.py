# tests/utils/test_sqlalchemy_connection.py
from unittest.mock import patch, Mock
import pytest
from sqlalchemy import text

from config.db_data import Data
from utils.sqlalchemy_connection import SQLAlchemyConnection


@pytest.fixture
def mock_sqlalchemy_connection():
    """Фикстура для создания экземпляра SQLAlchemyConnection."""
    return SQLAlchemyConnection()

def test_init(mock_sqlalchemy_connection):
    """Тест инициализации класса."""
    assert mock_sqlalchemy_connection.engine is None
    assert mock_sqlalchemy_connection.SessionLocal is None
    assert mock_sqlalchemy_connection.session is None

def test_connect(mock_sqlalchemy_connection):
    """Тест подключения к базе данных."""
    with patch('utils.sqlalchemy_connection.create_engine') as mock_create_engine:
        mock_sqlalchemy_connection.connect()
        mock_create_engine.assert_called_once_with(Data.DB_URL,pool_size=5,
            max_overflow=0,
            pool_recycle=3600)
        assert mock_sqlalchemy_connection.engine is not None
        assert mock_sqlalchemy_connection.SessionLocal is not None
        assert mock_sqlalchemy_connection.session is None

def test_get_session(mock_sqlalchemy_connection):
    """Тест получения сессии."""
    mock_sqlalchemy_connection.connect()
    session = mock_sqlalchemy_connection.get_session()
    assert session is not None

def test_disconnect(mock_sqlalchemy_connection):
    """Тест отключения от базы данных."""
    mock_sqlalchemy_connection.connect()
    session = mock_sqlalchemy_connection.get_session()
    mock_sqlalchemy_connection.disconnect()
    assert mock_sqlalchemy_connection.session is None
    assert mock_sqlalchemy_connection.engine is None
    assert mock_sqlalchemy_connection.SessionLocal is None

def test_execute_query_fetch_one(mock_sqlalchemy_connection):
    """Тест выполнения запроса с получением одной записи."""
    mock_sqlalchemy_connection.connect()
    query = text("SELECT 1")
    result = mock_sqlalchemy_connection.execute_query(query, fetch_one=True)
    """поскольку запрос возвращает только одно значение (1), результатом будет кортеж (1,)."""
    assert result == (1,)

def test_execute_query_fetch_all(mock_sqlalchemy_connection):
    """Тест выполнения запроса с получением всех записей."""
    mock_sqlalchemy_connection.connect()
    query = text("SELECT 1 UNION ALL SELECT 2")
    result = mock_sqlalchemy_connection.execute_query(query, fetch_all=True)
    """поскольку запрос возвращает две строки (1 и 2), результатом будет список [(1,), (2,)]."""
    assert result == [(1,), (2,)]
    assert len(result) == 2

def test_execute_query_commit(mock_sqlalchemy_connection):
    """Тест выполнения запроса с фиксацией транзакции."""
    mock_sqlalchemy_connection.connect()
    query = text("INSERT INTO some_table (value) VALUES (1)")
    mock_sqlalchemy_connection.execute_query(query, commit=True)

def test_execute_query_error(mock_sqlalchemy_connection):
    """Тест выполнения запроса с ошибкой."""
    mock_sqlalchemy_connection.connect()
    query = text("SELECT invalid_column FROM some_table")
    with patch('utils.custom_logger.CustomLogger.log_with_context') as mock_log:
        mock_sqlalchemy_connection.execute_query(query)
        assert mock_log.call_count == 2

def test_execute_query_fetch_one_and_all(mock_sqlalchemy_connection):
    """Тест выполнения запроса с одновременным использованием fetch_one и fetch_all."""
    mock_sqlalchemy_connection.connect()
    query = text("SELECT 1")
    with pytest.raises(ValueError):
        mock_sqlalchemy_connection.execute_query(query, fetch_one=True, fetch_all=True)

def test_get_session_without_connection(mock_sqlalchemy_connection):
    """Тест получения сессии без подключения к базе данных."""
    with pytest.raises(Exception):
        mock_sqlalchemy_connection.get_session()