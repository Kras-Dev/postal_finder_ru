# clients/postal_code_info.py

class PostalCodeInfo:
    """Класс для хранения и представления информации о почтовом коде."""
    def __init__(self, longitude:float, latitude:float, country:str, state:str) -> None:
        """Инициализация объекта PostalCodeInfo.

        :param longitude: Долгота, определяющая географическое расположение (тип: float).
        :param latitude: Широта, определяющая географическое расположение (тип: float).
        :param country: Название страны (тип: str).
        :param state: Название субъекта (штат, область и т.д., тип: str).
        """
        self.longitude = longitude
        self.latitude = latitude
        self.country = country
        self.state = state

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта PostalCodeInfo.
        Форматирует информацию о долготе, широте, стране и субъекте в удобочитаемом виде.

        :return: Строка, содержащая информацию о долготе, широте, стране и субъекте.
        """
        return (
            f"Долгота: {self.longitude},\n"
            f"Широта: {self.latitude},\n"
            f"Страна: {self.country},\n"
            f"Субъект: {self.state}"
        )