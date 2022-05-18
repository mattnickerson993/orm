from datetime import datetime, timezone
from models import Job, Message


if __name__ == "__main__":

     ########## where (filter) ###############
    # print(Message.objects)
    # msgs = Message.objects.where( id=1, content='newest content')
    # for msg in msgs:
    #     print(msg.id)
    #     print(msg.content)
    # msgs = Message.objects.all()
    # for msg in msgs:
    #     print(msg.id)
    #     print(msg.content)


     ########## get ###############
    # msg = Message.objects.get(content='individual message')
    # print(msg)
    # print(msg.id)
    # print(msg.content)
    # msg = Message.objects.get(id=4)
    # print(msg)
    # print(msg.id)
    # print(msg.content)


     ########## create ###############
    # msg = Message.objects.create(
    #     content = 'newly created content againn'
    # )
    # print(msg)
    # print(msg.id)
    # print(msg.content)

    ########## save (create or update) ###############
    # msg = Message(content='content to save')
    # msg.save()
    # print(msg.id)
    # print(msg.content)

    # msgs = Message.objects.where(content='content to save')
    # for msg in msgs:
    #     msg.content = 'modified content'
    #     msg.save()

    ########## delete ###############
    # msg = Message.objects.get(id=1)
    # msg.delete()

    ##############create table ################
    Job.objects.create_table()
    Message.objects.create_table()
    # Message.objects.create(
    #     content= 'test content',
    #     body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
    #          Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
    #     count = 7,
    #     tries = 5.5,
    #     date_created = datetime.now(timezone.utc)
    # )
    # Job.objects.create_table()
    # Job.objects.create(
    #     data='test data',
    #     body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
    #          Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
    #     count = 53,
    #     tries = 9.11,
    #     is_active = True,
    # )
    # job = Job.objects.get(id=1)
    # msg = Message.objects.get(id = 1)
    Message.objects.create(
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        date_created = datetime.now()
    )