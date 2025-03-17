# main.py

from utils.psycopg2_connection import Psycopg2Сonnection
from models.psycopg2_models import create_tables
from clients.psycopg2_client import Psycopg2Client

def main():

    # Создаем экземпляр DatabaseConnection
    conn = Psycopg2Сonnection()
    conn.connect()

    if conn.connection:
        create_tables()  # Мы уже подключились, поэтому просто вызываем функцию

        client = Psycopg2Client(conn)
        postal_code_to_select = "241014"
        result = client.select_postal_code(postal_code_to_select)
        print(result)
    else:
        print("Не удалось подключиться к базе данных.")

    # Обязательно отключаемся в конце работы
    conn.disconnect()


if __name__ == '__main__':
    main()
