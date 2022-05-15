from base_orm import Model
import fields

class Message(Model):

    _table_name = 'message'
        
    content = fields.CharField(max_length=255)
    body = fields.CharField(max_length=120, nullalbe=True)
    count = fields.IntegerField(nullalbe=True)
    tries = fields.IntegerField()

    def __str__(self):
        return f"{self.content}"


class Job(Model):

    _table_name = 'job'
        
    data = fields.CharField(max_length=255)

    def __str__(self):
        return f"{self.data}"