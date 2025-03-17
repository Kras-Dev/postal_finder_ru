# db/models/psycopg2_models.py

import psycopg2
from config.db_data import Data

# Проверяем наличие переменных окружения
Data.validate()
#Получает соединение с базой данных PostgreSQL
def connect_to_db():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(
            user = Data.DB_USER,
            password = Data.DB_PASS,
            host = Data.DB_HOST,
            port = Data.DB_PORT,
            database = Data.DB_NAME
        )
        print("Connected to PostgreSQL")
        return connection

    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
#Создает таблицы в базе данных, если их нет
def create_tables(connection):
    if connection is None:
        return
    # Создайте курсор для выполнения операций с базой данных
    cursor = connection.cursor()
    try:
        # SQL-запрос для создания новой таблицы
        create_table_query = '''
             CREATE TABLE IF NOT EXISTS postal_codes (
                post_code VARCHAR(10) PRIMARY KEY NOT NULL,
                country VARCHAR(60) NOT NULL,
                country_abbreviation VARCHAR(2) NOT NULL,
                place_name VARCHAR(100) NOT NULL,
                longitude FLOAT NOT NULL,
                state VARCHAR(255) NOT NULL,
                state_abbreviation VARCHAR(10),
                latitude FLOAT NOT NULL
            );
        '''
        # Выполнение команды: это создает новую таблицу
        cursor.execute(create_table_query)
        # Создание индекса для столбца post_code
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_code ON postal_codes (post_code);')

        create_table_query = '''
            CREATE TABLE IF NOT EXISTS postal_codes_requests_statistics (
                post_code INT PRIMARY KEY NOT NULL,
                request_count INT DEFAULT 0
            );
        '''
        cursor.execute(create_table_query)
        # Создание индекса для столбца postal_code в таблице postal_codes_requests_statistics
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_code ON postal_codes_requests_statistics (post_code);')
        connection.commit()
        print("Tables created successfully.")

    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed")


# Example usage:
# conn = connect_to_db()
# if conn:
#     create_tables(conn)
#     conn.close()

