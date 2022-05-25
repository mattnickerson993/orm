import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from base_orm import BaseManager, MetaModel
from models import Job, Message, User
from settings import DB_SETTINGS, TEST_DB_SETTINGS


@pytest.fixture(scope='session')
def test_client_db(create_test_db, models, test_db_connection):
    """
    creates test database and models and drops db at end of session
    lasts entire pytest session prior to teardown
    """
    BaseManager.connection = test_db_connection
    Job.objects.create_table()
    User.objects.create_table()
    Message.objects.create_table()
    models.append(Job)
    models.append(Message)
    models.append(User)
    yield models
    MetaModel.manager_class.connection.close()
    drop_test_db()
    return


@pytest.fixture(scope='session')
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
    connection.close()


@pytest.fixture(scope='session')
def models():
    return []


@pytest.fixture(scope='session')
def test_db_connection():
    connection = psycopg2.connect(
        dbname=TEST_DB_SETTINGS.get('DB_NAME'),
        user=TEST_DB_SETTINGS.get('DB_USER'),
        password=TEST_DB_SETTINGS.get('DB_PASS'),
        host=TEST_DB_SETTINGS.get('DB_HOST')
    )
    return connection


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
    return


@pytest.fixture(scope='function')
def cleanup(test_db_connection):
    """
    clears tables of all rows and resets all id sequences
    runs after each pytest test
    """

    cursor = test_db_connection.cursor()
    GET_TABLES_QUERY = """
    SELECT table_name FROM information_schema.tables
    WHERE table_schema='public' AND table_type='BASE TABLE';
    """
    cursor.execute(GET_TABLES_QUERY)
    res = cursor.fetchall()
    yield res
    DELETE_CONTENT_QUERY = "TRUNCATE {table} RESTART IDENTITY CASCADE;"
    for row in res:
        try:
            FINAL_DELETE_SQL = DELETE_CONTENT_QUERY.format(table=row[0])
            cursor.execute(FINAL_DELETE_SQL)
        except Exception as e:
            print(e)

    test_db_connection.commit()
    return
