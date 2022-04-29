import psycopg2
import pytest

from orm import Database, Message

from settings import DB_SETTINGS


def test_db_connect():
    db = Database(**DB_SETTINGS)
    assert isinstance(db.conn, psycopg2.extensions.connection)

def test_create_table(db):
    db.create_table(Message)
    assert Message._create_sql() == "CREATE TABLE IF NOT EXISTS messages_message (id SERIAL PRIMARY KEY, content VARCHAR);"

    # for table in ("author", "book"):
    #     assert table in db.tables