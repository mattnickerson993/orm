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

    # get

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
    # msg_from_db = db.get(Message, id=2, content='modified content')
    # sql, params = msg_from_db._get_update_sql()
    # msg_from_db.content = 'modified content again'
    # db.update(msg_from_db)

    # mod_msg = db.get(Message, id=2)
    # print(mod_msg.id)
    # print(mod_msg.content)
    

    # delete

    msg = db.get(Message, id=2)
    sql, params = msg._get_delete_sql()
    db.delete(msg)
    # msg = db.get(Message, id=2)
