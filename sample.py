from datetime import datetime, timezone
from models import Job, Message, User


if __name__ == "__main__":

#     ###### insert row with fk into messages ##########
#      User.objects.create_table()
#      Message.objects.create_table()
#      user = User.objects.create(
#         email='matt@email.com',
#         first_name='matt',
#         last_name='last',
#         is_active='true'
#     )

     # msg = Message.objects.create(
     #    content='my test content 2',
     #    body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
     #         Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
     #    count = 7,
     #    tries = 7.5,
     #    is_active = True,
     #    date_created = datetime.now()
     # )
     msgs = Message.objects.values_list('tries', flat=True)
     for msg in msgs:
          print(msg)