import os
import psycopg2
from urllib.parse import urlparse


class PGConnector:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def __setattr__(self, name, value):
        if name in ('host', 'database', 'user', 'password'):
            if type(value) != str:
                raise TypeError(f'{name} must be a string')
            else:
                object.__setattr__(self, name, value)
        elif name == 'port':
            if type(value) != int:
                raise TypeError('port must be an integer')
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def connect(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )


class HerokuDatabaseConnector:
    def __init__(self, os_var_name='DATABASE_URL', connector=PGConnector):
        self.url = os.environ[os_var_name]
        self.os_var_name = os_var_name
        self.connector = connector
        self.data = urlparse(self.url)

    def connect(self):
        self.connector = self.connector(
            host=self.data.hostname,
            port=self.data.port,
            database=self.data.path[1:],
            user=self.data.username,
            password=self.data.password
        )
        return self.connector.connect()
