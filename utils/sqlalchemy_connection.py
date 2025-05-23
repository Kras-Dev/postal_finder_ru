# utils/sqlalchemy_connection.py
from typing import Optional, Tuple, Any, Union, List, Mapping

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import Executable

from config.db_data import Data
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)


class SQLAlchemyConnection:
    """Класс для управления соединением с базой данных PostgresSQL с использованием SQLAlchemy.

      Этот класс предоставляет методы для подключения к базе данных, выполнения SQL-запросов,
      закрытия соединения и работы с сессиями.
      """

    def __init__(self) -> None:
        """Инициализация класса и создание движка базы данных.

            Создаем движок базы данных.\n
            Создаем фабрику сессий.\n
            Используем фабрику для создания новой сессии.
        """
        self.engine: Optional[create_engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self.session: Optional[Session] = None


    def connect(self) -> None:
        """Устанавливает соединение с базой данных, создавая движок SQLAlchemy и сеансовую фабрику."""

        """
        pool_size (int): Максимальное количество соединений, которые пул будет поддерживать открытыми.
        max_overflow (int): Максимальное количество соединений, которое пул может создать сверх pool_size. 
                           Если это значение равно 0, пул не будет переполняться.
        pool_recycle (int): Количество секунд, после которых соединение будет переработано. Это полезно для 
                           баз данных, которые отключают соединения после определенного периода бездействия.
        """
        try:
            Data.validate()
            self.engine = create_engine(Data.DB_URL, pool_size=5, max_overflow=0, pool_recycle=3600)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        except SQLAlchemyError as e:
            custom_logger.log_with_context(f"Error creating database engine: {e}")

    def get_session(self) -> Session:
        """Создает новую сессию для взаимодействия с базой данных.
            :return: Новая сессия SQLAlchemy."""
        if self.SessionLocal is None:
            raise Exception("SessionLocal is not initialized. Check database connection.")
        self.session = self.SessionLocal()
        custom_logger.log_with_context(f"Created new session, session_id: {id(self.session)}")
        return self.session

    def disconnect(self) -> None:
        """Закрывает движок базы данных и освобождает ресурсы.

        Если сессия открыта, она будет закрыта.
        """
        if self.session:
            custom_logger.log_with_context(f"Closed session {id(self.session)}")
            self.session.close()
            self.session = None
        if self.engine:
            self.engine.dispose()
            self.engine = None
        self.SessionLocal = None
        custom_logger.log_with_context("Disconnected from PostgresSQL")

    def execute_query(self,
                      query: Executable,
                      params: Optional[Mapping[str, Any]] = None,
                      fetch_one: bool = False,
                      fetch_all: bool = False,
                      commit: bool = False) -> Optional[Union[Tuple, List[Tuple]]]:
        """Выполняет SQL-запрос с передачей параметров и выбором режима получения данных.

        :param query: SQL-запрос для выполнения.
        :param params: Параметры запроса.
        :param fetch_one: Флаг для получения одной записи.
        :param fetch_all: Флаг для получения всех записей.
        :param commit: Флаг для фиксации транзакции.
        :return: Полученные данные из базы данных.
        """
        session = self.get_session()
        try:
            result = session.execute(query, params)

            if fetch_one and fetch_all:
                raise ValueError("You can't get fetch_one and fetch_all at the same time.")

            if commit:
                session.commit()
            elif fetch_one:
                return result.fetchone()
            elif fetch_all:
                """Приводим результат к списку кортежей"""
                return [tuple(row) for row in result.fetchall()]

        except SQLAlchemyError as e:
            custom_logger.log_with_context(f"Database error: {e}")
            if commit:
                session.rollback()

        finally:
            session.close()
