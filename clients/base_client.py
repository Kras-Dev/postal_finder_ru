#clients/base.client.py
from abc import ABC,abstractmethod


class BaseClient(ABC):
    """Абстрактный базовый класс для клиентов, работающих с базой данных."""

    @abstractmethod
    def insert_postal_code(self, postal_data: dict) -> None:
        """
           Вставляет данные о почтовом коде.

           :param postal_data: Словарь с данными о почтовом коде.
           :return: None
           """
        pass

    @abstractmethod
    def increment_request_statistic(self, postal_code: str) -> None:
        """
            Увеличивает статистику запросов для заданного почтового кода.

            :param postal_code: Строка, представляющая почтовый код.
            :return: None
            """
        pass