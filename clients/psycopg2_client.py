# db/models/psycopg2_client.py
import psycopg2

from db.models.psycopg2_models import connect_to_db

class Psycopg2Client:
    def __init__(self):
        self.connector = None
        self.cursor = None

    def connection(self):
        self.connector = connect_to_db()
        self.cursor = self.connector.cursor()

    def disconnection(self):
        if self.connector:
            self.cursor.close()
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
            return result

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
            self.cursor.execute(
                query,(
                    postal_data['post code'],
                    postal_data['country'],
                    postal_data['country abbreviation'],
                    postal_data['places'][0]['place name'],
                    postal_data['places'][0]['longitude'],
                    postal_data['places'][0]['latitude'],
                    postal_data['places'][0]['state'],
                    postal_data['places'][0]['state abbreviation']
                )
            )
            self.connector.commit()
            print(f"Inserted postal code {postal_data['post code']} into postal_codes")

        except psycopg2.Error as e:
            print(f"Error inserting postal code: {e}")
            self.connector.rollback()

        finally:
            self.disconnection()




