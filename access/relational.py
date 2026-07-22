"""Access to database."""

import os
from typing import Dict

import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError

class SQLAccess:

    def __int__(self):
        credentials: Dict[str, str] = self._get_credentials()
        self.database = credentials['database']
        self.user = credentials['user']
        self.password = credentials['password']
        self.host = credentials['host']
        self.port = credentials['port']

    def _get_credentials(self) -> Dict[str, str]:
        credentials: Dict[str, str] = {}
        # Load variables from the .env file into the environment
        load_dotenv()
        database: str = os.getenv('DATABASE')
        user: str = os.getenv('PY_USER')
        password: str = os.getenv('PASSWORD')
        host: str = os.getenv('HOST')
        port: str = os.getenv('PORT')
        credentials['database'] = database
        credentials['user'] = user
        credentials['password'] = password
        credentials['host'] = host
        credentials['port'] = port

        return credentials

    def create_connection(self):
        connection = None
        try:
            # Connect to your PostgresSQL database
            connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            print("Connection to PostgresSQL DB successful")

            # Create a cursor to execute SQL commands
            cursor = connection.cursor()

            # Run a test query (Fetch PostgresSQL version)
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"PostgresSQL version: {db_version[0]}")

            # Clean up the cursor
            cursor.close()

        except OperationalError as e:
            print(f"The error '{e}' occurred")

        finally:
            # Ensure the connection closes even if errors happen
            if connection is not None:
                connection.close()
                print("PostgresSQL connection is closed")