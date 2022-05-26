# orm

## About the project

As a python developer, I've worked heavily with Django and Flask and have
developed an interest in the object relational mappers that support them.
I set out to build a small version of an orm that emulates many of the features
django offers. My goals with undertaking this project included improving my understanding
of both orms and object oriented programming in python. The project uses pyscog2 and pytest
and is only compatible with postgres at this time.

## To run the project

Connect your postgres database via the Host, user, password and db name in the settings.py file.
For testing, you must connect via the same host , user and password but may set the test_db name
to any name you please.

## To run the tests

```
pytest test_orm.py

```

## Orm use

### Creating Tables/models

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

Once the tables are created. Methods are available that look similar to
the Django orm.

```
from datetime import datetime
from models import Message

### create row in table (Will autosave like django orm)

msg = Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count=7,
        tries=5.5,
        is_active=True,
        date_created=datetime.now()
    )

### another way to create row in table and save

    msg= Message(
        content='test content two',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count=77,
        tries=4.5,
        is_active=False,
        date_created=datetime.now()
    )
    msg.save()

### to update the model/row

 msg.count = 1
 msg.contet = 'updated content'
 msg.save()

 ### to get a single row/model from db
 msg = Message.objects.get(id=1, count=1)


 ### to delete a database row
 msg.delete()

```

#### Quersysets

4 methods are available that return querysets

1. all - returns a queryset with all db rows for model
2. where - returns a queryset filtered by given kwargs
3. values_list - returns a queryset of tuples with given args
4. values - returns a queryset with dictionaries composed of given args

```
 #all

 msgs = Message.objects.all()

 #where(similar to django filter)

 msgs = Message.objects.where(is_active=True, content='test content')

 #values_list

 msgs = Message.objects.values_list('id', 'is_active')

 # values_list flat (returns individual values rather than tuples)

 msgs = Message.objects.values_list('id', flat=True)

 #values

 msgs = Message.objects.values('id', 'is_active')

```

#### Quersyset chaining

Querysets are designed to function like the django orm where
the database is not hit until iteration. This allows chaining to take place.

2 additional methods may be utilized

- order_by -- returns and queryset ordered by stated args.
- count -- returns an integer counting all values in queryset

```
# examples of chaining

msgs = Message.objects.values_list('count', flat=True).order_by('id')

msgs = Message.objects.where(is_active=True).values('id', 'count', 'tries')

# -id means descending order
msgs = Message.objects.values('id', 'content').where(count=77).order_by('-id')

msgs = Message.objects.where(count=77).values_list('id', 'content').order_by('-id')

msgs = Message.objects.all().count()

msgs = Message.objects.where(id=2).order_by('-id').count()

msgs = Message.objects.where(count=77).order_by('-tries', '-id')

```

#### Fields available

#### Personal Growth

I really enjoyed taking a deeper look into python, django and orms in this project.
This project was built over roughly 1 month while working full time. I hope to build upon it
in the future with the goal of replicating features of other orms to understand them better
while also attempting to build unique features that may be of use.

#### Resources utilized

- [Django Docs](https://docs.djangoproject.com/en/4.0/topics/db/queries/)
- [TestDriven.io](https://testdriven.io/courses/python-web-framework/)
- [Hacksoft.io](https://www.hacksoft.io/blog/django-orm-under-the-hood-iterables)
- [Yannick KIKI](https://levelup.gitconnected.com/how-i-built-a-simple-orm-from-scratch-in-python-18b50108cfa3)
