# main.py

from models.psycopg2_models import connect_to_db, create_tables
from clients.psycopg2_client import Psycopg2Client
from clients.api_client import get_postal_data

def main():
    conn = connect_to_db()
    if conn:
        create_tables(conn)
    # Создаем экземпляр клиента
    client = Psycopg2Client()
#     postal_data = {
#       "post code": "141015",
#       "country": "Russia",
#       "country abbreviation": "RU",
#       "places": [
#         {
#           "place name": "Мытищи 15",
#           "longitude": "38.4267",
#           "state": "Московская Область",
#           "state abbreviation": "",
#           "latitude": "55.531"
#     }
#   ]
# }
#     # Вставка записи
#     client.insert_postal_code(postal_data)
    # Вывод записи
    postal_code_to_select = 663305
    result = client.select_postal_code(postal_code_to_select)
    print(f"{result}, type={type(result)}") #(38.4267, 55.531, 'Russia', 'Московская Область')
    api_data = get_postal_data("RU", postal_code_to_select)
    print(f"{api_data}, type={type(api_data)}")

    # if result:
    #     longitude, latitude, country, state = result
    #     print(
    #         f"Post Code: {postal_code_to_select}, Longitude: {longitude}, Latitude: {latitude}, Country: {country}, State: {state}")
    # else:
    #     print(f"No record found for post code {postal_code_to_select}")


if __name__ == '__main__':
    main()
