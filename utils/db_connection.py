# utils/db_connection.py

import psycopg2
from config.db_data import Data
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)
# Проверяем наличие переменных окружения
Data.validate()
#Получает соединение с базой данных PostgreSQL
def connect_to_db():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(
            user = Data.DB_USER,
            password = Data.DB_PASS,
            host = Data.DB_HOST,
            port = Data.DB_PORT,
            database = Data.DB_NAME
        )
        custom_logger.log_with_context(f"Connected to PostgreSQL conn:{id(connection)}")
        return connection

    except psycopg2.Error as e:
        custom_logger.log_with_context(f"Error connecting to the database: {e}")
        return None

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Устанавливает соединение с базой данных и создает курсор."""
        self.connection = connect_to_db()
        if self.connection is not None:
            self.cursor = self.connection.cursor()

    def disconnect(self):
        """Закрывает курсор и соединение."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            custom_logger.log_with_context(f"Closed connection {id(self.connection)}")
            self.connection.close()
        custom_logger.log_with_context("Disconnected from PostgreSQL")

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """
        Выполняет SQL-запрос к базе данных.

        :param query: SQL-запрос, который будет выполнен.
        :param params: Параметры для SQL-запроса (если они нужны). Тип: tuple или None (по умолчанию None)
            Описание: Параметры, которые будут подставлены в SQL-запрос. Например, если запрос содержит плейсхолдеры %s,
            можно использовать этот параметр для передачи значений, которые будут вставлены на их место.
        :param fetch_one: Флаг, указывающий, нужно ли возвращать одну строку (по умолчанию False).
        :param fetch_all: Флаг, указывающий, нужно ли возвращать все строки (по умолчанию False).
        :param commit: Флаг, указывающий, нужно ли выполнять commit для изменения данных (по умолчанию False). Тип: bool (по умолчанию False)
            Описание: Флаг, указывающий, нужно ли выполнять commit (подтверждать изменения) для модификационных запросов.
            Если этот параметр установлен в True, выполнится коммит после успешного выполнения запроса.
        :return: Результат запроса, если fetch_one=True, или fetch_all=True; None в противном случае.
        """
        try:
            if not self.connection:  # Если нет активного соединения, подключаемся
                self.connect()
            self.cursor.execute(query, params)
            if commit:
                self.connection.commit()
            if fetch_one:
                return self.cursor.fetchone()  # Возвращаем одну строку
            elif fetch_all:
                return self.cursor.fetchall()  # Возвращаем все строки
        except psycopg2.Error as e:
            custom_logger.log_with_context(f"Database error: {e}")
            if commit:
                self.connection.rollback()
