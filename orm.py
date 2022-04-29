import inspect
import psycopg2


class Database:
    def __init__(self, **kwargs):
        self.conn = psycopg2.connect(
            dbname=kwargs.get('DB_NAME'),
            user=kwargs.get('DB_USER'),
            password=kwargs.get('DB_PASS'),
            host=kwargs.get('DB_HOST')
        )
    
    def create_table(self, model):
        try:
            cur = self.conn.cursor()
            res = cur.execute(model._create_sql())
            print('res', res)
        except Exception as e:
            print(e)


class Model():
    def __init__(self):
        pass
    
    @classmethod
    def _create_sql(cls):
        CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS {table_name}s_{table_name} ({columns});"
        table_name = cls.__name__.lower()
        columns = ['id SERIAL PRIMARY KEY']
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                columns.append(f'{name} {field.sql_type}')
        final_sql = CREATE_TABLE_SQL.format(
            table_name=table_name, 
            columns=", ".join(columns))
        return final_sql
    
    @property
    def tables(self):
        SELECT_TABLES_SQL = """
        SELECT table_name FROM information_schema.tables
        WHERE table_type='BASE TABLE' AND table_schema='public';
        """
        return [x[0] for x in self.conn.execute(SELECT_TABLES_SQL).fetchall()]


class Column():
    def __init__(self, column_type):
        self.column_type = column_type
    
    @property
    def sql_type(self):
        SQL_TYPE_MAPPER = {
            int: "INTEGER",
            float: "REAL",
            str: "VARCHAR",
            bytes: "BLOB",
            bool: "INTEGER"
        }
        return SQL_TYPE_MAPPER[self.column_type]


class Message(Model):
    content = Column(str)