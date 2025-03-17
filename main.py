# main.py

from utils.db_connection import DatabaseConnection
from models.psycopg2_models import create_tables
from clients.psycopg2_client import Psycopg2Client

def main():
    # Создаем экземпляр DatabaseConnection
    connection = DatabaseConnection()
    connection.connect()

    if connection.connection:
        create_tables()  # Мы уже подключились, поэтому просто вызываем функцию

        client = Psycopg2Client(connection)
        postal_code_to_select = "663302"
        result = client.select_postal_code(postal_code_to_select)
        print(f"{result}, type={type(result)}")
    else:
        print("Не удалось подключиться к базе данных.")

    # Обязательно отключаемся в конце работы
    connection.disconnect()


if __name__ == '__main__':
    main()
