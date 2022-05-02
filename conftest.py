import pytest

from orm import Database, Model, Column
from settings import DB_SETTINGS

@pytest.fixture
def db():
    db = Database(**DB_SETTINGS)
    return db


@pytest.fixture
def Message():
    class Message(Model):
        content = Column(str)
    return Message