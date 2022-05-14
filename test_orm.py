import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pytest
from base_orm import Message
from exceptions import ModelNotFound, MultipleObjectsReturned
# from base_orm import Job, Message

from settings import DB_SETTINGS




def test_create_models(test_client_db, cleanup):
    Job, Message = test_client_db
    job = Job.objects.create(data='test data')
    msg = Message.objects.create(content='test content')
    assert job.id == 1
    assert msg.id == 1
    assert msg.content == 'test content'
    assert job.data == 'test data'

def test_get_models(test_client_db, cleanup):
    Job, Message = test_client_db
    Job.objects.create(data='test data')
    Message.objects.create(content='test content')
    job = Job.objects.get(id = 1)
    msg = Message.objects.get(id = 1)
    assert job.id == 1
    assert msg.id == 1
    assert msg.content == 'test content'
    assert job.data == 'test data'

def test_model_not_found_exception(test_client_db, cleanup):
    Job, _ = test_client_db
    with pytest.raises(ModelNotFound):
        job = Job.objects.get(id=100)


def test_multi_objs_exception(test_client_db, cleanup):
    Job, _ = test_client_db
    Job.objects.create(data='test data')
    Job.objects.create(data='test data')
    with pytest.raises(MultipleObjectsReturned):
        job = Job.objects.get(data='test data')


def test_all(test_client_db, cleanup):
    Job, _ = test_client_db
    Job.objects.create(data='test data')
    Job.objects.create(data='more test data')
    jobs = Job.objects.all()
    assert len(jobs) == 2


def test_where(test_client_db, cleanup):
    Job, Message = test_client_db
    Job.objects.create(data='test data')
    Message.objects.create(content='test content')
    Message.objects.create(content='test content')
    msgs = Message.objects.where(content = 'test content')
    ids = [msg.id for msg in msgs]
    assert ids == [1, 2]

def test_save(test_client_db, cleanup):
    Job, Message = test_client_db
    job = Job(
        data = 'data to save'
    )
    job.save()
    assert job.id == 1
    assert job.data == 'data to save'

def test_delete(test_client_db, cleanup):
    Job, _ = test_client_db
    job = Job(
        data = 'data to save'
    )
    job.save()
    assert job.id == 1
    assert job.data == 'data to save'
    job.delete()
    with pytest.raises(ModelNotFound):
        job = Job.objects.get(id=1)
    return