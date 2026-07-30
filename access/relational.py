"""Access to database."""

import os
from typing import Dict

import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError

class SQLAccess:

    def __init__(self):
        credentials: Dict[str, str] = self._get_credentials()
        self.database_url = credentials['database_url']
        self.user = credentials['user']
        self.password = credentials['password']

    def _get_credentials(self) -> Dict[str, str]:
        credentials: Dict[str, str] = {}
        # Load variables from the .env file into the environment
        load_dotenv()
        if os.getenv("ENV_MODE") == "development":
            load_dotenv(".env.dev", override=True)
            print("Operating in Local Development mode.")
        else:
            print("Operating in Neon Production mode.")
        database_url: str = os.getenv('DATABASE_URL')
        user: str = os.getenv('PY_USER')
        password: str = os.getenv('PASSWORD')
        credentials['database_url'] = database_url
        credentials['user'] = user
        credentials['password'] = password

        return credentials

    def create_connection(self):
        connection = None
        try:
            # Connect to your PostgresSQL database
            connection = psycopg2.connect(
                self.database_url,
                user=self.user,
                password=self.password,
            )
            print("Connection to PostgresSQL DB successful")

            # Create a cursor to execute SQL commands
            cursor = connection.cursor()

            # Run a test query (Fetch PostgresSQL version)
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"PostgresSQL version: {db_version[0]}")

            return cursor

        except OperationalError as e:
            print(f"The error '{e}' occurred")
            raise e

    def close_connection(self, cursor):
        try:
            cursor.connection.close()
            print("PostgresSQL connection is closed")

        except OperationalError as e:
            return f"The error '{e}' occurred"