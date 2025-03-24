# tests/utils/test_psycopg2_connection.py
from unittest.mock import patch, Mock

import pytest
from psycopg2 import Error

from config.db_data import Data
from utils.psycopg2_connection import Psycopg2Connection


@pytest.fixture
def mock_psycopg2_pool():
    """Фикстура для имитации подключения к базе данных."""
    with patch('psycopg2.pool.SimpleConnectionPool') as mock_pool:
        yield mock_pool
    mock_pool.reset_mock()

@pytest.fixture
def mock_psycopg2_cursor():
    """Фикстура для имитации курсора базы данных."""
    with patch('psycopg2.extensions.cursor') as mock_cursor:
        yield mock_cursor
    mock_cursor.reset_mock()

def test_init_psycopg2_connection():
    """Тестирование инициализации Psycopg2Connection."""
    conn = Psycopg2Connection()
    assert conn.connection_pool is None
    assert conn.connection is None
    assert conn.cursor is None

def test_connect_to_db_success(mock_psycopg2_pool):
    """Тестирование успешного подключения к базе данных."""
    mock_connection_pool = Mock()
    mock_psycopg2_pool.return_value = mock_connection_pool
    conn = Psycopg2Connection()
    result = conn.connect_to_db()
    assert result is mock_connection_pool
    mock_psycopg2_pool.assert_called_once_with(minconn=1,
        maxconn=5,
        user=Data.DB_USER,
        password=Data.DB_PASS,
        host=Data.DB_HOST,
        port=Data.DB_PORT,
        database=Data.DB_NAME
    )

def test_connect_to_db_failure(mock_psycopg2_pool):
    """Тестирование неуспешного подключения к базе данных."""
    mock_psycopg2_pool.side_effect = Error("Test error")
    conn = Psycopg2Connection()
    result = conn.connect_to_db()
    assert result is None
    mock_psycopg2_pool.assert_called_once_with(minconn=1,
        maxconn=5,
        user=Data.DB_USER,
        password=Data.DB_PASS,
        host=Data.DB_HOST,
        port=Data.DB_PORT,
        database=Data.DB_NAME
    )

def test_connect(mock_psycopg2_pool, mock_psycopg2_cursor):
    """Тестирование метода connect."""
    """
    mock_psycopg2_connect — это мок для функции psycopg2.connect, 
    которая используется для подключения к базе данных PostgreSQL.
    mock_psycopg2_pool — это мок для SimpleConnectionPool, который будет 
    использоваться для управления соединениями с базой данных.
    
    При вызове mock_psycopg2_pool() будет возвращен новый объект мок 
    (Mock()), который будет имитировать поведение пула соединений.
    """
    mock_connection_pool = Mock()
    mock_psycopg2_pool.return_value = mock_connection_pool
    mock_connection = Mock()
    mock_connection_pool.getconn.return_value = mock_connection
    conn = Psycopg2Connection()
    conn.connect()
    assert conn.connection is mock_connection
    assert conn.cursor is not None

def test_disconnect(mock_psycopg2_pool, mock_psycopg2_cursor):
    """Тестирование метода disconnect."""
    """
    mock_connection = mock_psycopg2_connect.return_value: присваиваем переменной mock_connection объект мок, 
    который возвращается при вызове mock_psycopg2_connect(). Это позволяет нам работать с этим объектом мок как с 
    объектом соединения с базой данных.
    """
    mock_connection_pool = Mock()
    mock_psycopg2_pool.return_value = mock_connection_pool
    mock_connection = Mock()
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection_pool = mock_connection_pool
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    conn.disconnect()
    mock_cursor.close.assert_called_once()
    mock_connection_pool.putconn.assert_called_once_with(mock_connection)

def test_execute_query_success(mock_psycopg2_pool, mock_psycopg2_cursor):
    """Тестирование успешного выполнения SQL-запроса."""
    mock_connection_pool = Mock()
    mock_psycopg2_pool.return_value = mock_connection_pool
    mock_connection = Mock()
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    query = "SELECT * FROM table"
    result = conn.execute_query(query, fetch_one=True)
    mock_cursor.execute.assert_called_once_with(query, None)
    assert result is mock_cursor.fetchone.return_value

def test_execute_query_failure(mock_psycopg2_pool, mock_psycopg2_cursor):
    """Тестирование неуспешного выполнения SQL-запроса."""
    mock_connection_pool = Mock()
    mock_psycopg2_pool.return_value = mock_connection_pool
    mock_connection = Mock()
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    mock_cursor.execute.side_effect = Error("Test error")
    query = "SELECT * FROM table"
    result = conn.execute_query(query, fetch_one=True)
    assert result is None
    mock_cursor.execute.assert_called_once_with(query, None)

def test_execute_query_commit(mock_psycopg2_pool, mock_psycopg2_cursor):
    """Тестирование выполнения SQL-запроса с commit."""
    mock_connection_pool = Mock()
    mock_psycopg2_pool.return_value = mock_connection_pool
    mock_connection = Mock()
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    query = "INSERT INTO table VALUES ('value')"
    conn.execute_query(query, commit=True)
    mock_cursor.execute.assert_called_once_with(query, None)
    mock_connection.commit.assert_called_once()

def test_execute_query_fetch_all(mock_psycopg2_pool, mock_psycopg2_cursor):
    """Тестирование выполнения SQL-запроса с fetch_all."""
    mock_connection_pool = Mock()
    mock_psycopg2_pool.return_value = mock_connection_pool
    mock_connection = Mock()
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    query = "SELECT * FROM table"
    result = conn.execute_query(query, fetch_all=True)
    mock_cursor.execute.assert_called_once_with(query, None)
    assert result is mock_cursor.fetchall.return_value

def test_execute_query_fetch_one_and_all(mock_psycopg2_pool, mock_psycopg2_cursor):
    """Тестирование выполнения SQL-запроса с fetch_one и fetch_all одновременно."""
    mock_connection_pool = Mock()
    mock_psycopg2_pool.return_value = mock_connection_pool
    mock_connection = Mock()
    mock_cursor = mock_psycopg2_cursor.return_value
    conn = Psycopg2Connection()
    conn.connection = mock_connection
    conn.cursor = mock_cursor
    query = "SELECT * FROM table"
    with pytest.raises(ValueError):
        conn.execute_query(query, fetch_one=True, fetch_all=True)