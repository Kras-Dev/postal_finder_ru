# models/sqlalchemy_client.py
from typing import Optional

from sqlalchemy import select

from clients.base_client import BaseClient
from clients.postal_code_info import PostalCodeInfo
from models.sqlalchemy_models import PostalCode, PostalCodeRequestStatistics
from utils.custom_logger import CustomLogger
from utils.sqlalchemy_connection import SQLAlchemyConnection

custom_logger = CustomLogger(__name__)

class SqlAlchemyClient(BaseClient):
    """ Клиент для взаимодействия с базой данных через SQLAlchemy."""
    def __init__(self, connection: SQLAlchemyConnection) -> None:
        """
        Инициализация клиента с соединением с базой данных.

        :param connection: Соединение с базой данных.
        """
        self.connection = connection
        self.session = connection.get_session()

    def select_postal_code(self, postal_code) -> Optional[PostalCodeInfo]:
        """
        Получение информации о почтовом коде из базы данных или API.

        Если почтовый код не найден в базе данных, то происходит запрос к API.

        :param postal_code: Почтовый код для поиска.
        :return: Информация о почтовом коде или None, если не найдено.
        """

        postal_info = self.get_postal_code_from_db(postal_code)
        if not postal_info:
            from service.api_db_service import ApiDBService
            return ApiDBService(self).fetch_postal_code_from_api(postal_code)
        return postal_info

    def get_postal_code_from_db(self, postal_code: str)-> Optional[PostalCodeInfo]:
        """
        Получение информации о почтовом коде из базы данных.

        :param postal_code: Почтовый код для поиска.
        :return: Информация о почтовом коде или None, если не найдено.
        """
        query = select(PostalCode.longitude, PostalCode.latitude, PostalCode.country, PostalCode.state).where(
            PostalCode.post_code == str(postal_code))
        with self.session as session:
            result = session.execute(query).fetchone()
        if result is None:
            custom_logger.log_with_context(f"No postal data {postal_code} found in database")
            return None
        postal_info = PostalCodeInfo(*result)
        self.increment_request_statistic(postal_code)
        return postal_info

    def insert_postal_code(self, postal_data: dict) -> None:
        """
        Вставка информации о почтовых данных в базу данных.

        :param postal_data: Словарь с информацией о почтовых данных.
        """
        postal_info = PostalCode(
            post_code=postal_data['post code'],
            country=postal_data['country'],
            country_abbreviation=postal_data['country abbreviation'],
            place_name=postal_data['places'][0]['place name'],
            longitude=postal_data['places'][0]['longitude'],
            latitude=postal_data['places'][0]['latitude'],
            state=postal_data['places'][0]['state'],
            state_abbreviation=postal_data['places'][0]['state abbreviation']
        )
        with self.session as session:
            session.add(postal_info)
            session.commit()

    def increment_request_statistic(self, postal_code: str) -> None:
        """Обновляет или создает запись статистики запросов для заданного почтового кода.
               :param postal_code: Строка, представляющая почтовый код, для которого необходимо обновить статистику."""

        with self.session as session:
            # statistic = session.execute(
            #     select(PostalCodeRequestStatistics).where(PostalCodeRequestStatistics.post_code == postal_code)
            # ).scalars().first()
            statistic = session.query(PostalCodeRequestStatistics).filter_by(post_code=postal_code).first()
            if statistic:
                statistic.request_count += 1
            else:
                statistic = PostalCodeRequestStatistics(post_code=postal_code, request_count=1)
                session.add(statistic)

            session.commit()