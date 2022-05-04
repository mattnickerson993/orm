from orm import Database, Message
from settings import DB_SETTINGS

if __name__ == "__main__":
    db = Database(**DB_SETTINGS)
    sql, vals = Message._get_single_row_sql(id=1, content='individual')
    print('sql', sql)
    print('vals', vals)
    # msg = Message(content='individual message')
    # db.save(msg)

    # msg_from_db = db.get(Message, id=1)