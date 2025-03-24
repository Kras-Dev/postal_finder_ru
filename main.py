# main.py

from clients.sqlalchemy_client import SqlAlchemyClient
from utils.psycopg2_connection import Psycopg2Connection
from clients.psycopg2_client import Psycopg2Client
from utils.sqlalchemy_connection import SQLAlchemyConnection

def main():
    while True:
        postal_code = input("\nВведите почтовый индекс (или 'exit' для выхода): ").strip()
        if postal_code.lower() == 'exit':
            break

        client_type = input("Выберите клиент (1 - Psycopg2, 2 - SQLAlchemy): ").strip()

        if client_type == '1':
            """Обработка через Psycopg2"""
            conn = Psycopg2Connection()
            try:
                conn.connect()
                if conn.connection:
                    client = Psycopg2Client(conn)
                    result = client.select_postal_code(postal_code)
                    print("Результат Psycopg2:", result)
                else:
                    print("Не удалось подключиться к базе данных через Psycopg2")
            except Exception as e:
                print(f"Ошибка Psycopg2: {str(e)}")
            finally:
                conn.disconnect()

        elif client_type == '2':
            """Обработка через SQLAlchemy"""
            conn = SQLAlchemyConnection()
            try:
                conn.connect()
                client = SqlAlchemyClient(conn)
                result = client.select_postal_code(postal_code)
                print("Результат SQLAlchemy:", result)
            except Exception as e:
                print(f"Ошибка SQLAlchemy: {str(e)}")
            finally:
                conn.disconnect()

        else:
            print("Неверный выбор клиента. Введите 1 или 2")



if __name__ == '__main__':
    main()
