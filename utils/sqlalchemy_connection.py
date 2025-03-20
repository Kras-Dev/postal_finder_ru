#utils/sqlalchemy_connection.py
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
        Data.validate()
        try:
            self.engine = create_engine(Data.DB_URL)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.session: Optional[Session] = None
        except SQLAlchemyError as e:
            custom_logger.log_with_context(f"Error creating database engine: {e}")

    def get_session(self) -> Session:
        """Создает новую сессию для взаимодействия с базой данных.
            :return: Новая сессия SQLAlchemy."""
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
                # Приводим результат к списку кортежей
                return [tuple(row) for row in result.fetchall()]

        except SQLAlchemyError as e:
            custom_logger.log_with_context(f"Database error: {e}")
            if commit:
                session.rollback()

        finally:
            session.close()
