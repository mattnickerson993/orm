# orm

## About the project

As a python developer, I worked heavily with Django and Flask and have
developed an interest in the object relational mappers that support them.
I set out to build a small version of an orm that emulates many of the features
django offers. My goals with undertaking this project included improving my understanding
of both orms and object oriented programming in python. The project uses pyscog2 and pytest
and is only compatible with postgres at this time.

## To run the project

Connect your postgres database via the Host, user, password and db name in the settings.py file.
For testing, you must connect via the same host , user and password but may set the test_db name
to any name you please.

### To run the tests

```
pytest test_orm.py

```

### Orm use

#### Creating Tables/models

1. Create a model (samples are found in the models.py file)

models.py

```
class User(Model):

    email = fields.CharField(max_length=255)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255)
    is_active = fields.BooleanField()
    date_joined = fields.DateTimeField(nullable=True, default=datetime.now(timezone.utc))

    def __str__(self):
        return f"{self.email}"

class Message(Model):

    content = fields.CharField(max_length=255)
    body = fields.TextField(nullable=True)
    count = fields.IntegerField(nullable=True)
    tries = fields.FloatField(nullable=True)
    is_active = fields.BooleanField(default=True)
    date_created = fields.DateTimeField(nullable=True)
    user = fields.ForeignKey(User, nullable=True, on_delete='SET NULL')

    def __repr__(self):
        return f"{self.content}"

    def __str__(self):
        return f"{self.content}"
```

2. Import model and create database table

```
from models import Message, User

User.objects.create_table()
Message.objects.create_table()

```

#### CRUD functionality
