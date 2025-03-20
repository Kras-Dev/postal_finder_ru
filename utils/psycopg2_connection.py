# utils/psycopg2_connection.py
from typing import Optional, Tuple, Any, Union, List

import psycopg2
from config.db_data import Data
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)
Data.validate()


class Psycopg2Connection:
    """Класс для управления соединением с базой данных PostgresSQL с использованием библиотеки psycopg2.
    Этот класс предоставляет методы для подключения к базе данных, выполнения SQL-запросов, закрытия соединения и курсора.    """
    def __init__(self) -> None:
        """метод устанавливает значение атрибутов connection и cursor в None."""
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None

    def connect_to_db(self) -> Optional[psycopg2.extensions.connection]:
        """Устанавливает соединение с базой данных PostgresSQL
            :return: connection: Возвращает объект соединения с базой данных, или None в случае ошибки."""
        try:
            connection = psycopg2.connect(
                user=Data.DB_USER,
                password=Data.DB_PASS,
                host=Data.DB_HOST,
                port=Data.DB_PORT,
                database=Data.DB_NAME
            )
            custom_logger.log_with_context(f"Connected to PostgresSQL conn:{id(connection)}")
            return connection

        except psycopg2.Error as e:
            custom_logger.log_with_context(f"Error connecting to the database: {e}")
            return None

    def connect(self) -> None:
        """Устанавливает соединение с базой данных и создает курсор."""
        self.connection = self.connect_to_db()
        if self.connection is not None:
            self.cursor = self.connection.cursor()

    def disconnect(self) -> None:
        """Закрывает курсор и соединение."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            custom_logger.log_with_context(f"Closed connection {id(self.connection)}")
            self.connection.close()
        custom_logger.log_with_context("Disconnected from PostgresSQL")

    def execute_query( self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        commit: bool = False) -> Optional[Union[Tuple, List[Tuple]]]:
        """
        Выполняет SQL-запрос к базе данных.

        :param query: SQL-запрос, который будет выполнен.
        :param params: Параметры для SQL-запроса (если они нужны). Тип: tuple, содержащий элементы любого типа (Any),
            и ... указывает на то, что кортеж может иметь произвольное количество элементов или None (по умолчанию None)
            Описание: Параметры, которые будут подставлены в SQL-запрос. Например, если запрос содержит плейсхолдеры %s,
            можно использовать этот параметр для передачи значений, которые будут вставлены на их место.
        :param fetch_one: Флаг, указывающий, нужно ли возвращать одну строку (по умолчанию False).
        :param fetch_all: Флаг, указывающий, нужно ли возвращать все строки (по умолчанию False).
        :param commit: Флаг, указывающий, нужно ли выполнять commit для изменения данных (по умолчанию False).
        :return: Метод возвращает `Optional[Union[Tuple, List[Tuple]]]`, он может вернуть результат запроса одну строку (кортеж),
            если `fetch_one=True`, или все строки (список кортежей), если `fetch_all=True`; `None` в противном случае.
        """
        try:
            if not self.connection:  # Если нет активного соединения, подключаемся
                self.connect()
            self.cursor.execute(query, params)
            if fetch_one and fetch_all:
                raise ValueError("Cannot fetch both one and all rows at the same time.")
            if commit:
                self.connection.commit()
            elif fetch_one:
                return self.cursor.fetchone()  # Возвращаем одну строку
            elif fetch_all:
                return self.cursor.fetchall()  # Возвращаем все строки

        except psycopg2.Error as e:
            custom_logger.log_with_context(f"Database error: {e}")
            if commit:
                self.connection.rollback()


