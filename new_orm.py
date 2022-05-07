from base_orm import Model, Column


class Message(Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    content = Column(str)

    def __str__(self):
        return f"{self.content}"


if __name__ == '__main__':
    msg = Message(content='test')
    print(msg.db.conn)
    # msg2 = Message(content='test2')
    # msgs = Message.db.all()
    # for msg in msgs:
    #     print(msg)

    # msg = Message.db.conn