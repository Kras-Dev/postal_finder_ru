#service/api_db_service.py
from typing import Optional

from clients.postal_code_info import PostalCodeInfo
from clients.psycopg2_client import Psycopg2Client
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)

class ApiDBService:
    def __init__(self, psycopg2_client: Optional[Psycopg2Client]) -> None:
        self.psycopg2_client = psycopg2_client

    def fetch_postal_code_from_api(self, postal_code: str) -> Optional[PostalCodeInfo]:
        """Получить данные о почтовом коде из API и сохранить в БД."""
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


