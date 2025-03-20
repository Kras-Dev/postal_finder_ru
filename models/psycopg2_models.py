# models/psycopg2_models.py
import psycopg2

from utils.psycopg2_connection import Psycopg2Connection
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)

class Psycopg2Models:
    def __init__(self) -> None:
        """Класс предоставляет методы для создания таблиц."""
        self.conn = Psycopg2Connection()

    def create_tables(self) -> None:
        """Создает таблицы в базе данных, если их нет"""
        self.conn.connect()

        if self.conn.connection is None:
            custom_logger.log_with_context("No valid connection provided.")
            return
        try:
            create_table_query = '''
                 CREATE TABLE IF NOT EXISTS postal_codes (
                    post_code VARCHAR(10) PRIMARY KEY NOT NULL,
                    country VARCHAR(60) NOT NULL,
                    country_abbreviation VARCHAR(10) NOT NULL,
                    place_name VARCHAR(100) NOT NULL,
                    longitude FLOAT NOT NULL,
                    state VARCHAR(255) NOT NULL,
                    state_abbreviation VARCHAR(10),
                    latitude FLOAT NOT NULL
                );
            '''
            # Выполнение команды: это создает новую таблицу
            self.conn.cursor.execute(create_table_query)

            create_table_query = '''
                CREATE TABLE IF NOT EXISTS postal_codes_requests_statistics (
                    post_code VARCHAR(10) PRIMARY KEY NOT NULL,
                    request_count INT DEFAULT 0
                );
            '''
            self.conn.cursor.execute(create_table_query)
            self.conn.connection.commit()
            custom_logger.log_with_context("Tables created successfully.")

        except psycopg2.Error as e:
            custom_logger.log_with_context(f"Error creating tables: {e}")

        finally:
            self.conn.disconnect()

