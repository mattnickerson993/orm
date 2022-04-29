import pytest

from orm import Database
from settings import DB_SETTINGS

@pytest.fixture
def db():
    db = Database(**DB_SETTINGS)
    return db