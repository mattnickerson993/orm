from orm import Database, Message
from settings import DB_SETTINGS

if __name__ == "__main__":
    db = Database(**DB_SETTINGS)
    # sql, fields, vals = Message._get_single_row_sql(id=1, content='individual')
    # print(sql)
    # print(fields)
    # print(vals)
    # msg = Message(content='individual message')
    # db.save(msg)

    # msg_from_db = db.get(Message, id=2, content='individual message')
    # msgs = db.all(Message)
    # for msg in msgs:
    #     print(msg)
    #     print(msg.id)
    #     print(msg.content)
    # print(msg_from_db)
    # print(type(msg_from_db))
    # print('id', msg_from_db.id)
    # print('content', msg_from_db.content)


    # update
    msg_from_db = db.get(Message, id=2, content='individual message')
    msg_from_db.content = 'modified content'
    db.update(msg_from_db)
    