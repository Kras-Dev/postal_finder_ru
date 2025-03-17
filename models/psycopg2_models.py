# models/psycopg2_models.py
import logging
import psycopg2

from utils.db_connection import DatabaseConnection
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)


#Создает таблицы в базе данных, если их нет
def create_tables():
    connection = DatabaseConnection()
    connection.connect()

    if connection.connection is None:
        custom_logger.log_with_context("No valid connection provided.")
        return
    try:
        # SQL-запрос для создания новой таблицы
        create_table_query = '''
             CREATE TABLE IF NOT EXISTS postal_codes (
                post_code VARCHAR(10) PRIMARY KEY NOT NULL,
                country VARCHAR(60) NOT NULL,
                country_abbreviation VARCHAR(2) NOT NULL,
                place_name VARCHAR(100) NOT NULL,
                longitude FLOAT NOT NULL,
                state VARCHAR(255) NOT NULL,
                state_abbreviation VARCHAR(10),
                latitude FLOAT NOT NULL
            );
        '''
        # Выполнение команды: это создает новую таблицу
        connection.cursor.execute(create_table_query)
        # Создание индекса для столбца post_code
        connection.cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_code ON postal_codes (post_code);')

        create_table_query = '''
            CREATE TABLE IF NOT EXISTS postal_codes_requests_statistics (
                post_code VARCHAR(10) PRIMARY KEY NOT NULL,
                request_count INT DEFAULT 0
            );
        '''
        connection.cursor.execute(create_table_query)
        # Создание индекса для столбца postal_code в таблице postal_codes_requests_statistics
        connection.cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_code ON postal_codes_requests_statistics (post_code);')
        connection.connection.commit()
        custom_logger.log_with_context("Tables created successfully.")

    except psycopg2.Error as e:
        custom_logger.log_with_context(f"Error creating tables: {e}")

    finally:
        connection.disconnect()

