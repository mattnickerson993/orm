from datetime import datetime, timezone
from base_orm import Model
import fields

class Message(Model):

    _table_name = 'message'
        
    content = fields.CharField(max_length=255)
    body = fields.TextField(nullable=True)
    count = fields.IntegerField(nullable=True)
    tries = fields.FloatField(nullable=True)
    is_active = fields.BooleanField(default=True)
    date_created = fields.DateTimeField(nullable=True)



    def __str__(self):
        return f"{self.content}"


class Job(Model):

    _table_name = 'job'
        
    data = fields.CharField(max_length=255)
    body = fields.TextField(nullable=True)
    count = fields.IntegerField(nullable=True)
    tries = fields.FloatField(nullable=True)
    is_active = fields.BooleanField()
    date_created = fields.DateTimeField(nullable=True, default=datetime.now(timezone.utc))

    def __str__(self):
        return f"{self.data}"