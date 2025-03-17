# db/models/psycopg2_client.py
import psycopg2

from models.psycopg2_models import connect_to_db

class PostalCodeInfo:
    def __init__(self, longitude, latitude, country, state):
        self.longitude = longitude
        self.latitude = latitude
        self.country = country
        self.state = state

    def __str__(self):
        return (f"Долгота: {self.longitude}, "
                f"Широта: {self.latitude}, "
                f"Страна: {self.country}, "
                f"Субъект: {self.state}")

class Psycopg2Client:
    def __init__(self):
        self.connector = None
        self.cursor = None

    def connection(self):
        self.connector = connect_to_db()
        self.cursor = self.connector.cursor()

    def disconnection(self):
        if self.cursor:
            self.cursor.close()
        if self.connector:
            self.connector.close()
        print("Disconnected from PostgreSQL")

    def select_postal_code(self, postal_code):
        query = '''
            SELECT longitude, latitude, country, state
            FROM postal_codes
            WHERE post_code = %s;                
        '''
        try:
            self.connection()
            self.cursor.execute(query, (postal_code,))
            result = self.cursor.fetchone()
            if result:
                longitude, latitude, country, state = result
                postal_info = PostalCodeInfo(longitude, latitude, country, state)
                return postal_info

        except psycopg2.Error as e:
            print(f"Error searching postal code: {e}")
            return None
        finally:
            self.disconnection()

    def insert_postal_code(self, postal_data):
        query = '''
            INSERT INTO postal_codes 
            (post_code, country, country_abbreviation, place_name, longitude, latitude, state, state_abbreviation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        '''
        try:
            self.connection()
            for place in postal_data['places']:
                self.cursor.execute(
                    query,
                    (
                        postal_data['post code'],
                        postal_data['country'],
                        postal_data['country abbreviation'],
                        place['place name'],
                        place['longitude'],
                        place['latitude'],
                        place['state'],
                        place['state abbreviation']
                    )
                )
            self.connector.commit()
            print(f"Inserted postal codes for {postal_data['post code']} into postal_codes")

        except psycopg2.Error as e:
            print(f"Error inserting postal code: {e}")
            self.connector.rollback()

        finally:
            self.disconnection()

    def increment_request_statistic(self, postal_code):
        query_select = '''
            SELECT 1 FROM postal_codes_requests_statistics WHERE postal_code = %s
        '''
        query_update = '''
            UPDATE postal_codes_requests_statistics
            SET request_count = request_count + 1
            WHERE postal_code = %s
        '''
        query_insert = '''
            INSERT INTO postal_codes_requests_statistics (postal_code, request_count)
            VALUES (%s, 1)
        '''
        try:
            self.connection()
            self.cursor.execute(query_select, (postal_code,))
            result = self.cursor.fetchone()
            if result:
                self.cursor.execute(query_update, (postal_code,))
            else:
                self.cursor.execute(query_insert, (postal_code,1 ,))
            self.connector.commit()
            print(f"Incremented request count statistics for postal code {postal_code}")
        except psycopg2.Error as e:
            print(f"Error incrementing request count statistics: {e}")
            self.connector.rollback()
        finally:
            self.disconnection()





