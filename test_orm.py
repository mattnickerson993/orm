import psycopg2
import pytest

from orm import Database

from settings import DB_SETTINGS


def test_db_connect():
    db = Database(**DB_SETTINGS)
    assert isinstance(db.conn, psycopg2.extensions.connection)

def test_create_table(db, Message):
    db.create_table(Message)
    assert Message._create_sql() == "CREATE TABLE IF NOT EXISTS messages_message (id SERIAL PRIMARY KEY, content VARCHAR);"


# def test_create_message_instance(db, Message):
#     msg = Message(content='test message creation')
#     db.save(msg)
#     assert msg._get_insert_sql() == (
#         "INSERT INTO messages_message (content) VALUES (%s) RETURNING id;",
#         ['test message creation']
#     )
#     assert msg.id == 1


def test_select_all_msgs(db, Message):
    msg_one = Message(content='first message')
    msg_two = Message(content='second message')
    db.save(msg_one)
    db.save(msg_two)

    msgs = db.all(Message)
    sql, cols = Message._get_select_all_sql()

    assert sql == 'SELECT id, content FROM messages_message;'
    assert cols == ['id', 'content']    

    assert len(msgs) == 2

    assert type(msgs[0]) == Message
    assert {msg.content for msg in msgs} == {'first message', 'second message'}