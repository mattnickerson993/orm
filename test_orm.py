from this import d

import psycopg2
from orm import Database

from settings import DB_SETTINGS


def test_db_connect():
    db = Database(**DB_SETTINGS)
    assert isinstance(db.conn, psycopg2.extensions.connection)

def test_create_table():
    pass