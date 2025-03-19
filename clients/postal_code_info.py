# clients/postal_code_info.py

class PostalCodeInfo:
    def __init__(self, longitude:float, latitude:float, country:str, state:str) -> None:
        self.longitude = longitude
        self.latitude = latitude
        self.country = country
        self.state = state

    def __str__(self) -> str:
        return (
            f"Долгота: {self.longitude},\n"
            f"Широта: {self.latitude},\n"
            f"Страна: {self.country},\n"
            f"Субъект: {self.state}"
        )