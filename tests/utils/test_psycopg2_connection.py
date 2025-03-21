# tests/utils/test_psycopg2_connection.py
from unittest.mock import patch, Mock

import pytest
from psycopg2 import Error

from config.db_data import Data
from utils.psycopg2_connection import Psycopg2Connection


@pytest.fixture
def mock_psycopg2_connect():
    """Фикстура для имитации подключения к базе данных."""
    with patch('psycopg2.connect') as mock_connect:
        yield mock_connect
    mock_connect.reset_mock()

@pytest.fixture
def mock_psycopg2_cursor():
    """Фикстура для имитации курсора базы данных."""
    with patch('psycopg2.extensions.cursor') as mock_cursor:
        yield mock_cursor
    mock_cursor.reset_mock()

def test_init_psycopg2_connection():
    """Тестирование инициализации Psycopg2Connection."""
    conn = Psycopg2Connection()
    assert conn.connection is None
    assert conn.cursor is None

def test_connect_to_db_success(mock_psycopg2_connect):
    """Тестирование успешного подключения к базе данных."""
    mock_psycopg2_connect.return_value = Mock()
    conn = Psycopg2Connection()
    result = conn.connect_to_db()
    assert result is not None
    mock_psycopg2_connect.assert_called_once_with(
        user=Data.DB_USER,
        password=Data.DB_PASS,
        host=Data.DB_HOST,
        port=Data.DB_PORT,
        database=Data.DB_NAME
    )

def test_connect_to_db_failure(mock_psycopg2_connect):
    """Тестирование неуспешного подключения к базе данных."""
    mock_psycopg2_connect.side_effect = Error("Test error")
    conn = Psycopg2Connection()
    result = conn.connect_to_db()
    assert result is None
    mock_psycopg2_connect.assert_called_once_with(
        user=Data.DB_USER,
        password=Data.DB_PASS,
        host=Data.DB_HOST,
        port=Data.DB_PORT,
        database=Data.DB_NAME
    )

def test_connect(mock_psycopg2_connect, mock_psycopg2_cursor):
    """Тестирование метода connect."""
    """mock_psycopg2_connect — это мок для функции psycopg2.connect, которая используется для подключения к 
        базе данных PostgreSQL.
        return_value = Mock() означает, что при вызове mock_psycopg2_connect() будет возвращен новый объект мок (Mock()).
        Этот объект мок будет имитировать поведение объекта соединения с базой данных."""
    mock_psycopg2_connect.return_value = Mock()
    mock_psycopg2_cursor.return_value = Mock()
    conn = Psycopg2Connection()
    conn.connect()
    assert conn.connection is not None
    assert conn.cursor is not None

def test_disconnect(mock_psycopg2_connect, mock_psycopg2_cursor):
    """Тестирование метода disconnect."""
    """mock_connection = mock_psycopg2_connect.return_value: присваиваем переменной mock_connection объект мок, 
        который возвращается при вызове mock_psycopg2_connect(). Это позволяет нам работать с этим объектом мок как с 
        объектом соединения с базой данных. """
    mock_connection = mock_psycopg2_connect.return_value
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    conn.disconnect()
    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()

def test_execute_query_success(mock_psycopg2_connect, mock_psycopg2_cursor):
    """Тестирование успешного выполнения SQL-запроса."""
    mock_connection = mock_psycopg2_connect.return_value
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    query = "SELECT * FROM table"
    result = conn.execute_query(query, fetch_one=True)
    mock_cursor.execute.assert_called_once_with(query, None)
    assert result is mock_cursor.fetchone.return_value

def test_execute_query_failure(mock_psycopg2_connect, mock_psycopg2_cursor):
    """Тестирование неуспешного выполнения SQL-запроса."""
    mock_connection = mock_psycopg2_connect.return_value
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    mock_cursor.execute.side_effect = Error("Test error")
    query = "SELECT * FROM table"
    result = conn.execute_query(query, fetch_one=True)
    assert result is None
    mock_cursor.execute.assert_called_once_with(query, None)

def test_execute_query_commit(mock_psycopg2_connect, mock_psycopg2_cursor):
    """Тестирование выполнения SQL-запроса с commit."""
    mock_connection = mock_psycopg2_connect.return_value
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    query = "INSERT INTO table VALUES ('value')"
    conn.execute_query(query, commit=True)
    mock_cursor.execute.assert_called_once_with(query, None)
    mock_connection.commit.assert_called_once()

def test_execute_query_fetch_all(mock_psycopg2_connect, mock_psycopg2_cursor):
    """Тестирование выполнения SQL-запроса с fetch_all."""
    mock_connection = mock_psycopg2_connect.return_value
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    query = "SELECT * FROM table"
    result = conn.execute_query(query, fetch_all=True)
    mock_cursor.execute.assert_called_once_with(query, None)
    assert result is mock_cursor.fetchall.return_value

def test_execute_query_fetch_one_and_all(mock_psycopg2_connect, mock_psycopg2_cursor):
    """Тестирование выполнения SQL-запроса с fetch_one и fetch_all одновременно."""
    mock_connection = mock_psycopg2_connect.return_value
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    query = "SELECT * FROM table"
    with pytest.raises(ValueError):
        conn.execute_query(query, fetch_one=True, fetch_all=True)