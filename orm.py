import psycopg2


class Database:
    def __init__(self, **kwargs):
        self.conn = psycopg2.connect(
            dbname=kwargs.get('DB_NAME'),
            user=kwargs.get('DB_USER'),
            password=kwargs.get('DB_PASS'),
            host=kwargs.get('DB_HOST')
        )
        print(type(self.conn))
    
    def create(self, table):
        self.conn.execute(table._create_sql())

class Model():
    def __init__(self):
        pass
    
    @classmethod
    def _create_sql(self):
        pass


class Course(Model):
    def __init__(self, column_type):
        self.column_type = column_type
    
    @property
    def sql_type(self):
        SQL_TYPE_MAPPER = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB",
            bool: "INTEGER"
        }
        return SQL_TYPE_MAPPER[self.column_type]


