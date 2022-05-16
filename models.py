from base_orm import Model
import fields

class Message(Model):

    _table_name = 'message'
        
    content = fields.CharField(max_length=255)
    body = fields.TextField(nullalbe=True)
    count = fields.IntegerField(nullalbe=True)
    tries = fields.FloatField(nullalbe=True)
    is_active = fields.BooleanField()
    date_created = fields.DateTimeField(nullalbe=True)



    def __str__(self):
        return f"{self.content}"


class Job(Model):

    _table_name = 'job'
        
    data = fields.CharField(max_length=255)
    body = fields.TextField(nullalbe=True)
    count = fields.IntegerField(nullalbe=True)
    tries = fields.FloatField(nullalbe=True)
    is_active = fields.BooleanField()
    date_created = fields.DateTimeField(nullalbe=True)

    def __str__(self):
        return f"{self.data}"