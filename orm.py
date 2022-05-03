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
        cur = self.conn.cursor()
        res = cur.execute(model._create_sql())
        self.conn.commit()
        
    def save(self, instance):
        cur = self.conn.cursor()
        sql, vals = instance._get_insert_sql()
        cur.execute(sql, vals)
        res = cur.fetchone()
        instance._data['id'] = res[0]
        self.conn.commit()


class Model:
    def __init__(self, **kwargs):
        self._data = {
            "id": None
        }
        for key, value in kwargs.items():
            self._data[key] = value
    
    def __getattribute__(self, key):
        _data = super().__getattribute__("_data")
        if key in _data:
            return _data[key]
        return super().__getattribute__(key)

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


    def _get_insert_sql(self):
        INSERT_SQL = "INSERT INTO {table_name}s_{table_name} ({column_names}) VALUES ({placeholders}) RETURNING id;"
        cls = self.__class__
        cols = []
        values = []
        placeholders = []
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, Column):
                cols.append(name)
                values.append(getattr(self, name))
                placeholders.append('%s')
        cols = ", ".join(cols)
        placeholders = ", ".join(placeholders)
        sql = INSERT_SQL.format(table_name=cls.__name__.lower(), column_names=cols, placeholders=placeholders)
        return sql, values

    @property
    def tables(self):
        SELECT_TABLES_SQL = """
        SELECT table_name FROM information_schema.tables
        WHERE table_type='BASE TABLE' AND table_schema='public';
        """
        return [x[0] for x in self.conn.execute(SELECT_TABLES_SQL).fetchall()]


class Column:
    def __init__(self, column_type):
        self.type = column_type
    
    @property
    def sql_type(self):
        SQL_TYPE_MAPPER = {
            int: "INTEGER",
            float: "REAL",
            str: "VARCHAR",
            bytes: "BLOB",
            bool: "INTEGER"
        }
        return SQL_TYPE_MAPPER[self.type]


class Message(Model):
    content = Column(str)