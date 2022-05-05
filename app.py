from orm import Database, Message
from settings import DB_SETTINGS

if __name__ == "__main__":
    db = Database(**DB_SETTINGS)
    # sql, fields, vals = Message._get_single_row_sql(id=1, content='individual')
    # msg = Message(content='indiv message')
    # db.save(msg)

    msg_from_db = db.get(Message, content='individual message', id=1)
    print(msg_from_db)
    print(type(msg_from_db))
    print('id', msg_from_db.id)
    print('content', msg_from_db.content)
