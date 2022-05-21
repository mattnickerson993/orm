from datetime import datetime, timedelta, timezone
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import NotNullViolation
import pytest
from exceptions import ModelNotFound, MultipleObjectsReturned
from fields import IntegerField
from models import Job, Message

from settings import DB_SETTINGS




def test_create_models(test_client_db, cleanup):
    Job, Message, *rest = test_client_db
    job = Job.objects.create(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        is_active = True,
        date_created = datetime.now()
    )
    msg = Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        is_active = True,
        date_created = datetime.now()
    )
    assert job.id == 1
    assert msg.id == 1
    assert msg.content == 'test content'
    assert job.data == 'test data'
    assert job.tries == 5.5
    assert msg.is_active == True
    assert job.count == 7
    assert type(job.date_created) == datetime

def test_get_models(test_client_db, cleanup):
    Job, Message, *rest = test_client_db
    Job.objects.create(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        is_active = True,
        date_created = datetime.now()
    )
    Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        is_active = True,
        date_created = datetime.now()
    )
    job = Job.objects.get(id = 1)
    msg = Message.objects.get(id = 1)
    assert job.id == 1
    assert msg.id == 1
    assert msg.content == 'test content'
    assert job.data == 'test data'
    assert job.count == 7
    assert msg.tries < 6.0

def test_model_not_found_exception(test_client_db, cleanup):
    Job, *rest = test_client_db
    with pytest.raises(ModelNotFound):
        job = Job.objects.get(id=100)


def test_multi_objs_exception(test_client_db, cleanup):
    Job, *rest = test_client_db
    Job.objects.create(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        is_active = True,
        date_created = datetime.now()
    )
    Job.objects.create(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        is_active = True,
        date_created = datetime.now()
    )
    with pytest.raises(MultipleObjectsReturned):
        job = Job.objects.get(data='test data')


def test_all(test_client_db, cleanup):
    Job, *rest = test_client_db
    Job.objects.create(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 77,
        tries = 8.5,
        is_active = False,
        date_created = datetime.now(timezone.utc) - timedelta(days=1)
    )
    Job.objects.create(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 53,
        tries = 9.11,
        is_active = True,
        date_created = datetime.now(timezone.utc) - timedelta(days=7)
    )
    jobs = Job.objects.all()
    assert len(jobs) == 2


def test_where(test_client_db, cleanup):
    Job, Message, *rest = test_client_db
    Job.objects.create(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 53,
        tries = 9.11,
        is_active = True,
        date_created = datetime.now(timezone.utc) - timedelta(days=7)
    )
    Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        is_active = True,
        date_created = datetime.now()
    )
    Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 120,
        tries = 1.5,
        is_active = True,
        date_created = datetime.now(timezone.utc)
    )
    msgs = Message.objects.where(content = 'test content')
    ids = [msg.id for msg in msgs]
    assert ids == [1, 2]

def test_save(test_client_db, cleanup):
    Job, Message, *rest = test_client_db
    job = Job(
        data='data to save',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 53,
        tries = 9.11,
        is_active = True,
        date_created = datetime.now(timezone.utc) - timedelta(days=7)
    )
    job.save()
    assert job.id == 1
    assert job.data == 'data to save'
    assert job.count == 53
    assert type(job.count) == int

def test_delete(test_client_db, cleanup):
    Job, *rest = test_client_db
    job = Job(
        data='data to save',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 53,
        tries = 9.11,
        is_active = True,
        date_created = datetime.now(timezone.utc) - timedelta(days=7)
    )
    job.save()
    assert job.id == 1
    assert job.data == 'data to save'
    job.delete()
    with pytest.raises(ModelNotFound):
        job = Job.objects.get(id=1)
    return

# def test_not_nullable(test_client_db, cleanup):
#     _, Message = test_client_db
#     with pytest.raises(NotNullViolation):
#         Message.objects.create(
#             body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
#                 Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
#             count = 7,
#             tries = 5.5,
#             is_active = True,
#             date_created = datetime.now(timezone.utc)
#         )

def test_default_values(test_client_db, cleanup):
    Job, Message, *rest = test_client_db
    Job.objects.create(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 53,
        tries = 9.11,
        is_active = True,
    )
    Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now()
    )
    msg = Message.objects.get(id=1)
    job = Job.objects.get(id = 1)
    assert msg.id == 1
    assert job.id == 1
    assert job.date_created <= datetime.now(timezone.utc)
    assert msg.is_active == True


def test_save_with_default_value(test_client_db, cleanup):
    Job, Message, *rest = test_client_db
    job = Job(
        data='test data',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 53,
        tries = 9.11,
        is_active = True,
    )
    job.save()
    assert job.id == 1
    assert job.date_created <= datetime.now(timezone.utc)
    same_job = Job.objects.get(id=1)
    same_job.is_active = False
    same_job.save()
    assert same_job.id == 1
    assert same_job.is_active != True

    msg = Message(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now()
    )
    msg.save()
    new_msg = Message.objects.get(id=1)
    assert new_msg.id == msg.id
    assert new_msg.is_active == msg.is_active

def test_fk_create(test_client_db, cleanup):
    _, Message, User = test_client_db
    user = User.objects.create(
        email='matt@email.com',
        first_name='matt',
        last_name='last',
        is_active='true'
    )
    msg = Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now(),
        user_id=user.id
    )

    assert user.email == 'matt@email.com'
    assert user.id == 1
    assert msg.content == 'test content'
    assert msg.user_id == 1

def test_fk_save(test_client_db, cleanup):
    _, Message, User = test_client_db
    user = User(
        email='matt@email.com',
        first_name='matt',
        last_name='last',
        is_active='true'
    )
    user.save()
    msg = Message(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now(),
        user_id=user.id
    )
    msg.save()
    assert user.email == 'matt@email.com'
    assert user.id == 1
    assert msg.content == 'test content'
    assert msg.user_id == 1


def test_fk_where(test_client_db, cleanup):
    _, Message, User = test_client_db
    user = User(
    email='matt1@email.com',
    first_name='matt1',
    last_name='last1',
    is_active='true'
    )
    user.save()
    msg = Message(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now(),
        user_id=user.id
    )
    msg.save()
    user2 = User.objects.create(
        email='matt2@email.com',
        first_name='matt2',
        last_name='last2',
        is_active='true'
    )
    msg = Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 77,
        tries = 6.5,
        date_created = datetime.now(),
        user_id=user2.id
    )
    msgs = Message.objects.where(content = 'test content')

    for msg in msgs:
        assert msg.user_id < 3
    assert len(msgs) == 2


def test_fk_all(test_client_db, cleanup):
    _, Message, User = test_client_db
    user = User(
    email='matt1@email.com',
    first_name='matt1',
    last_name='last1',
    is_active='true'
    )
    user.save()
    msg = Message(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now(),
        user_id=user.id
    )
    msg.save()
    user2 = User.objects.create(
        email='matt2@email.com',
        first_name='matt2',
        last_name='last2',
        is_active='true'
    )
    msg = Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 77,
        tries = 6.5,
        date_created = datetime.now(),
        user_id=user2.id
    )
    msgs = Message.objects.all()

    for msg in msgs:
        assert msg.user_id < 3
    assert len(msgs) == 2

def test_fk_save_mult(test_client_db, cleanup):
    _, Message, User = test_client_db
    user = User(
    email='matt1@email.com',
    first_name='matt1',
    last_name='last1',
    is_active='true'
    )
    user.save()
    msg = Message(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now(),
        user_id=user.id
    )
    msg.save()
    assert msg.id == 1
    assert msg.user_id == 1
    user2 = User.objects.create(
        email='matt2@email.com',
        first_name='matt2',
        last_name='last2',
        is_active='true'
    )
    msg.user_id = user2.id
    msg.save()

    assert msg.id == 1
    assert msg.user_id == 2



def test_fk_get(test_client_db, cleanup):
    _, Message, User = test_client_db
    user = User.objects.create(
        email='matt@email.com',
        first_name='matt',
        last_name='last',
        is_active='true'
    )
    msg = Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now(),
        user_id=user.id
    )
    user2 = User.objects.create(
        email='matt2@email.com',
        first_name='matt2',
        last_name='last2',
        is_active='true'
    )
    msg2 = Message.objects.create(
        content='test content two',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 77,
        tries = 5.5,
        date_created = datetime.now(),
        user_id=user2.id
    )
    my_msg = Message.objects.get(id = 1)
    assert my_msg.id == 1
    my_second_msg = Message.objects.get(user_id=2)
    assert my_second_msg.id == 2
    assert my_second_msg.tries == 5.5
    assert my_second_msg.user_id == 2

def test_fk_delete(test_client_db, cleanup):
    _, Message, User = test_client_db
    user = User.objects.create(
        email='matt@email.com',
        first_name='matt',
        last_name='last',
        is_active='true'
    )
    msg = Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now(),
        user_id=user.id
    )
    user.delete()
    msg.delete()
    with pytest.raises(ModelNotFound):
        my_msg = Message.objects.get(user_id=1)
    