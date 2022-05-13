import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pytest
from base_orm import Message
from exceptions import ModelNotFound
# from base_orm import Job, Message

from settings import DB_SETTINGS




def test_create_models(test_client_db):
    Job, Message = test_client_db
    job = Job.objects.create(data='test data')
    msg = Message.objects.create(content='test content')
    assert job.id == 1
    assert msg.id == 1
    assert msg.content == 'test content'
    assert job.data == 'test data'

def test_get_models(test_client_db):
    Job, Message = test_client_db
    job = Job.objects.get(id = 1)
    msg = Message.objects.get(id = 1)
    assert job.id == 1
    assert msg.id == 1
    assert msg.content == 'test content'
    assert job.data == 'test data'

def test_model_not_found_exception(test_client_db):
    Job, _ = test_client_db
    with pytest.raises(ModelNotFound):
        job = Job.objects.get(id=100)