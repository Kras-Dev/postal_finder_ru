# clients/api_client.py

import requests
from utils.custom_logger import CustomLogger
from typing import Optional, Dict, Any

custom_logger = CustomLogger(__name__)

class ApiClient:
    def get_postal_data(self, post_code: str) -> Optional[Dict[str, Any]]: # Указывает, что функция может вернуть либо словарь
        # (где ключи — строки и значения могут быть любого типа), либо None, когда данные не были получены из API.
        """Получить данные о почтовом коде из API."""
        url = f"https://api.zippopotam.us/RU/{post_code}"
        try:
            response = requests.get(url)
            """Метод raise_for_status() используется для проверки ответа HTTP на наличие ошибок. Он выполняет следующее:
                - Если статус-код ответа указывает на успешное выполнение запроса (например, 200 OK), 
                метод просто возвращает управление без каких-либо действий.
                - Если статус-код указывает на ошибку (например, 404 Not Found или 500 Internal Server Error), метод 
                вызывает исключение requests.exceptions.HTTPError."""
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            custom_logger.log_with_context(f"Error fetching data from API: {e}")
            return None