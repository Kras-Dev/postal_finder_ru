# main.py

from db.models.psycopg2_models import connect_to_db, create_tables
from db.clients.psycopg2_client import Psycopg2Client

def main():
    conn = connect_to_db()
    if conn:
        create_tables(conn)
    # Создаем экземпляр клиента
    client = Psycopg2Client()
    # postal_data = {
    #     "post code": "241014",
    #     "country": "Russia",
    #     "country abbreviation": "RU",
    #     "places": [{
    #         "place name": "Брянск 14",
    #         "longitude": "76.9133",
    #         "state": "Брянская Область",
    #         "state abbreviation": "",
    #         "latitude": "48.1699"
    #     }]
    # }
    # # Вставка записи
    # client.insert_postal_code(postal_data)
    # Вывод записи
    postal_code_to_select = 241014
    result = client.select_postal_code(postal_code_to_select)
    if result:
        longitude, latitude, country, state = result
        print(
            f"Post Code: {postal_code_to_select}, Longitude: {longitude}, Latitude: {latitude}, Country: {country}, State: {state}")
    else:
        print(f"No record found for post code {postal_code_to_select}")


if __name__ == '__main__':
    main()
