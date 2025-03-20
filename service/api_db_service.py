#service/api_db_service.py
from typing import Optional

from clients.postal_code_info import PostalCodeInfo
from clients.psycopg2_client import Psycopg2Client
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)

class ApiDBService:
    """Класс ApiDBService предназначен для получения данных о почтовых кодах из API и
       их сохранения в базе данных."""
    def __init__(self, psycopg2_client:Psycopg2Client) -> None:
        """Инициализирует ApiDBService с клиентом базы данных.
            :param psycopg2_client: Экземпляр Psycopg2Client для взаимодействия с базой данных.
            :return: None """
        self.psycopg2_client = psycopg2_client

    def fetch_postal_code_from_api(self, postal_code: str) -> Optional[PostalCodeInfo]:
        """Получает данные о почтовом коде из API и сохраняет их в базе данных.
            :param postal_code: Почтовый код, для которого необходимо получить данные.
            :return: Метод возвращает Optional[PostalCodeInfo]: объект PostalCodeInfo с данными о почтовом коде, если запрос успешен;
            иначе возвращает None, если данные не были получены."""
        from clients.api_client import ApiClient
        postal_data = ApiClient().get_postal_data(postal_code)
        if postal_data:
            self.psycopg2_client.insert_postal_code(postal_data)
            self.psycopg2_client.increment_request_statistic(postal_code)
            return PostalCodeInfo(
                postal_data['places'][0]['longitude'],
                postal_data['places'][0]['latitude'],
                postal_data['country'],
                postal_data['places'][0]['state']
            )
        else:
            custom_logger.log_with_context(f"No postal data found from API for {postal_code}")
            return None


