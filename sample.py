from datetime import datetime, timezone
from models import Job, Message, User


if __name__ == "__main__":

#     ###### insert row with fk into messages ##########
     # User.objects.create_table()
     # Message.objects.create_table()
     # user = User.objects.get(id=1)

     msg = Message.objects.create(
        content='test content',
        body='Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
             Phasellus condimentum ex a risus aliquet venenatis.consectetur adipiscing elit.',
        count = 7,
        tries = 5.5,
        is_active = True,
        date_created = datetime.now()
     )
     print(msg.user)