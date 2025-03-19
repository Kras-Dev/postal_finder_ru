# models/psycopg2_client.py
from typing import Optional

from utils.custom_logger import CustomLogger
from clients.postal_code_info import PostalCodeInfo
from utils.psycopg2_connection import Psycopg2Connection

custom_logger = CustomLogger(__name__)

class Psycopg2Client:
    def __init__(self,  connection: Psycopg2Connection) -> None:
        self.connection = connection

    def select_postal_code(self, postal_code: str) -> Optional[PostalCodeInfo]:
        """Получить информацию о почтовом коде из БД или API."""
        postal_info = self.get_postal_code_from_db(postal_code)
        if not postal_info:
            from service.api_db_service import ApiDBService
            return ApiDBService(self).fetch_postal_code_from_api(postal_code)
        return postal_info

    def get_postal_code_from_db(self, postal_code: str) -> Optional[PostalCodeInfo]:
        """Получить информацию о почтовом коде из БД."""
        query = '''
            SELECT longitude, latitude, country, state
            FROM postal_codes
            WHERE post_code = %s;                
        '''
        result = self.connection.execute_query(query, (postal_code, ), fetch_one=True)
        if result:
            longitude, latitude, country, state = result  # Извлекаем данные результата
            postal_info = PostalCodeInfo(longitude, latitude, country, state)  # Создаем объект PostalCodeInfo
            self.increment_request_statistic(postal_code)  # Увеличиваем счётчик запросов
            return postal_info  # Возвращаем информацию о почтовом коде
        else:
            custom_logger.log_with_context(f"No postal data {postal_code} found in database")
            return None

    def insert_postal_code(self, postal_data: dict) -> None:
        """Вставить данные о почтовом коде в БД."""
        query = '''
            INSERT INTO postal_codes 
            (post_code, country, country_abbreviation, place_name, longitude, latitude, state, state_abbreviation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        '''
        self.connection.execute_query(query, (
            postal_data['post code'],
            postal_data['country'],
            postal_data['country abbreviation'],
            postal_data['places'][0]['place name'],
            postal_data['places'][0]['longitude'],
            postal_data['places'][0]['latitude'],
            postal_data['places'][0]['state'],
            postal_data['places'][0]['state abbreviation']
        ), commit=True)

    def increment_request_statistic(self, postal_code: str) -> None:
        """Обновить или создать запись статистики запросов."""
        query_select = '''
            SELECT 1 FROM postal_codes_requests_statistics WHERE post_code = %s
        '''
        result = self.connection.execute_query(query_select, (postal_code,), fetch_one=True)  # Проверяем существование записи

        query_update = '''
            UPDATE postal_codes_requests_statistics
            SET request_count = request_count + 1
            WHERE post_code = %s
        '''
        query_insert = '''
            INSERT INTO postal_codes_requests_statistics (post_code, request_count)
            VALUES (%s, 1)
        '''
        if result:
            self.connection.execute_query(query_update, (postal_code,), commit=True)  # Обновляем существующую запись
        else:
            self.connection.execute_query(query_insert, (postal_code,), commit=True)  # Создаем новую запись





