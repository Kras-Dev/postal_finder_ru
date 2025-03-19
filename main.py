# main.py

from utils.psycopg2_connection import Psycopg2Connection
from clients.psycopg2_client import Psycopg2Client

def main():
    conn = Psycopg2Connection()
    conn.connect()

    if conn.connection:
        client = Psycopg2Client(conn)
        postal_code_to_select = "185028"
        result = client.select_postal_code(postal_code_to_select)
        print(result)
    else:
        print("Не удалось подключиться к базе данных.")
    conn.disconnect()


if __name__ == '__main__':
    main()
