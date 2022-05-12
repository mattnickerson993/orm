from this import d
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pytest

from orm import Database

from settings import DB_SETTINGS

def create_test_db():
    connection = psycopg2.connect(
            dbname=DB_SETTINGS.get('DB_NAME'),
            user=DB_SETTINGS.get('DB_USER'),
            password=DB_SETTINGS.get('DB_PASS'),
            host=DB_SETTINGS.get('DB_HOST')
        )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    CREATE_DB_SQL = """CREATE DATABASE test_db;"""
    cursor.execute(CREATE_DB_SQL)

def drop_test_db():
    connection = psycopg2.connect(
            dbname=DB_SETTINGS.get('DB_NAME'),
            user=DB_SETTINGS.get('DB_USER'),
            password=DB_SETTINGS.get('DB_PASS'),
            host=DB_SETTINGS.get('DB_HOST')
        )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    DELETE_DB_SQL = """DROP DATABASE test_db;"""
    cursor.execute(DELETE_DB_SQL)

# create_test_db()
# drop_test_db()