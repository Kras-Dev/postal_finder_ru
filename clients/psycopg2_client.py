# models/psycopg2_client.py

from clients.api_client import get_postal_data
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)

class PostalCodeInfo:
    def __init__(self, longitude, latitude, country, state):
        self.longitude = longitude
        self.latitude = latitude
        self.country = country
        self.state = state

    def __str__(self):
        return (
            f"Долгота: {self.longitude},\n"
            f"Широта: {self.latitude},\n"
            f"Страна: {self.country},\n"
            f"Субъект: {self.state}"
        )

class Psycopg2Client:
    def __init__(self, connection):
        self.connection = connection

    def select_postal_code(self, postal_code):
        # SQL-запрос для получения данных о почтовом коде
        query = '''
            SELECT longitude, latitude, country, state
            FROM postal_codes
            WHERE post_code = %s;                
        '''
        result = self.connection.execute_query(query, (postal_code, ), fetch_one=True)  # Выполняем запрос
        if result:
            longitude, latitude, country, state = result  # Извлекаем данные результата
            postal_info = PostalCodeInfo(longitude, latitude, country, state)  # Создаем объект PostalCodeInfo
            self.increment_request_statistic(postal_code)  # Увеличиваем счётчик запросов
            return postal_info  # Возвращаем информацию о почтовом коде
        else:
            custom_logger.log_with_context(f"No postal data {postal_code} found in database")
            postal_data = get_postal_data(postal_code)  # Запрашиваем данные из API
            if postal_data:
                self.insert_postal_code(postal_data)  # Вставляем данные в БД
                self.increment_request_statistic(postal_code)  # Увеличиваем счётчик запросов
                return PostalCodeInfo(
                    postal_data['places'][0]['longitude'],
                    postal_data['places'][0]['latitude'],
                    postal_data['country'],
                    postal_data['places'][0]['state']
                )
            else:
                custom_logger.log_with_context("No postal data found from API")
                return None

    def insert_postal_code(self, postal_data):
        # SQL-запрос для вставки данных о почтовом коде
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
        ), commit=True)  # Вставляем данные и подтверждаем изменения

    def increment_request_statistic(self, postal_code):
        # SQL-запрос для проверки, существует ли запись статистики запросов
        query_select = '''
            SELECT 1 FROM postal_codes_requests_statistics WHERE post_code = %s
        '''
        result = self.connection.execute_query(query_select, (postal_code,), fetch_one=True)  # Проверяем существование записи

        # SQL-запрос для обновления или вставки записи статистики
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





