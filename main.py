# main.py

from clients.sqlalchemy_client import SqlAlchemyClient
from utils.psycopg2_connection import Psycopg2Connection
from clients.psycopg2_client import Psycopg2Client
from utils.sqlalchemy_connection import SQLAlchemyConnection

def main():
    postal_code_to_select = "183008"

    # Подключение через Psycopg2
    conn = Psycopg2Connection()
    try:
        conn.connect()
        if conn.connection:
            client = Psycopg2Client(conn)
            result = client.select_postal_code(postal_code_to_select)
            print(result)
        else:
            print("Не удалось подключиться к базе данных.")
    except Exception as e:
        print(f"Ошибка при подключении через Psycopg2: {e}")
    finally:
        conn.disconnect()

    # Подключение через SQLAlchemy
    conn1 = SQLAlchemyConnection()
    try:
        client1 = SqlAlchemyClient(conn1)
        result1 = client1.select_postal_code(postal_code_to_select)
        print(result1)
    except Exception as e:
        print(f"Ошибка при подключении через SQLAlchemy: {e}")
    finally:
        conn1.disconnect()



if __name__ == '__main__':
    main()
