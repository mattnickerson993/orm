import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from orm import Database, Model, Column
from settings import DB_SETTINGS, TEST_DB_SETTINGS
import inspect
from base_orm import BaseManager, MetaModel, Job, Message
from collections import OrderedDict
# @pytest.fixture
# def db():
#     db = Database(**DB_SETTINGS)
#     return db


# @pytest.fixture
# def Message():
#     class Message(Model):
#         content = Column(str)
#     return Message

# destroyed at end of test session -- creates test database and models and drops db at end of session
@pytest.fixture(scope='session')
def models():
    return []

@pytest.fixture(scope='session')
def test_client_db(models):
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
    MetaModel.manager_class = BaseManager.set_connection(TEST_DB_SETTINGS)
    Job.objects.create_table()
    Message.objects.create_table()
    models.append(Job)
    models.append(Message)
    yield models
    MetaModel.manager_class.connection.close()
    DELETE_DB_SQL = """DROP DATABASE test_db;"""
    cursor.execute(DELETE_DB_SQL)
    return


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