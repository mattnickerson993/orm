from collections import OrderedDict
import inspect
import psycopg2

from exceptions import ModelNotFound, MultipleObjectsReturned


class Database:
    def __init__(self, **kwargs):
        self.conn = psycopg2.connect(
            dbname=kwargs.get('DB_NAME'),
            user=kwargs.get('DB_USER'),
            password=kwargs.get('DB_PASS'),
            host=kwargs.get('DB_HOST')
        )
    
    def all(self, model):
        cur = self.conn.cursor()
        sql, cols = model._get_select_all_sql()
        cur.execute(sql)
        res = []
        for row in cur.fetchall():
            instance = model()
            for field, value in zip(cols, row):
                setattr(instance, field, value)
            res.append(instance)          
        return res

    def create_table(self, model):
        cur = self.conn.cursor()
        res = cur.execute(model._create_sql())
        self.conn.commit()

    
    def delete(self, model):
        cur = self.conn.cursor()
        sql, params = model._get_delete_sql()
        res = cur.execute(sql, params)
        self.conn.commit()


    def get(self, model, **kwargs):
        sql, fields, params = model._get_single_row_sql(**kwargs)
        cur = self.conn.cursor()
        cur.execute(sql, params)
        res = cur.fetchall()
        num_rows = len(res)

        if num_rows > 1:
            raise MultipleObjectsReturned(f"Call to model manager expected 1 object, call returned {num_rows}!")
        elif not num_rows:
            raise ModelNotFound('No objects returned from query')
        
        instance = model()
        for field, val in zip(fields, res[0]):
            setattr(instance, field, val)
        return instance
    

        
    def save(self, instance):
        cur = self.conn.cursor()
        sql, vals = instance._get_insert_sql()
        cur.execute(sql, vals)
        res = cur.fetchone()
        instance._data['id'] = res[0]
        self.conn.commit()


    def update(self, instance):
        cur = self.conn.cursor()
        sql, vals = instance._get_update_sql()
        cur.execute(sql, vals)
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
    
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in self._data:
            self._data[name] = value


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
    
    def _get_delete_sql(self):
        DELETE_SQL = "DELETE from {table_name}s_{table_name} WHERE id = %s"
        cls = self.__class__
        values = [getattr(self, 'id')]
        FINAL_SQL = DELETE_SQL.format(table_name=cls.__name__.lower())
        return FINAL_SQL, values


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

    @classmethod
    def _get_select_all_sql(cls):
        SELECT_ALL_SQL = "SELECT {columns} FROM {table_name}s_{table_name};"
        table_name = cls.__name__.lower()
        cols = ['id']
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, Column):
                cols.append(name)
        
        sql = SELECT_ALL_SQL.format(columns=", ".join(cols), table_name=table_name)
        return sql, cols

    @classmethod
    def _get_single_row_sql(cls, **kwargs):
        INITIAL_SQL = """
        SELECT {fields} FROM {table_name}s_{table_name}
        WHERE {criteria};
        """ 
        table_name = cls.__name__.lower()

        # get all cls attributes only
        fields = [i[0] for i in inspect.getmembers(cls) 
                       if not i[0].startswith('_')
                       if not inspect.ismethod(i[1]) and not isinstance(i[1], property)]
                    
        if 'id' not in fields:
            fields.insert(0, 'id')
        cols = OrderedDict(**kwargs)
        criteria = [name for name in cols.keys()]
        values = [val for  val in cols.values()]
        FINAL_SQL = INITIAL_SQL.format(
            fields = ", ".join(fields),
            table_name=table_name,
            criteria=f"{'=%s AND '.join(criteria)}=%s"
        )
    
        return FINAL_SQL, fields, values


    @property
    def tables(self):
        SELECT_TABLES_SQL = """
        SELECT table_name FROM information_schema.tables
        WHERE table_type='BASE TABLE' AND table_schema='public';
        """
        return [x[0] for x in self.conn.execute(SELECT_TABLES_SQL).fetchall()]

    
    def _get_update_sql(self):
        UPDATE_SQL = "UPDATE {table_name}s_{table_name} SET {fields} WHERE id = %s"
        cls = self.__class__
        cols = []
        values = []
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, Column):
                cols.append(name)
                values.append(getattr(self, name))
        
        values.append(getattr(self, 'id'))

        FINAL_SQL = UPDATE_SQL.format(
            table_name=cls.__name__.lower(),
            fields=", ".join([f"{col} = %s" for col in cols])
            )

        return FINAL_SQL, values


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

    def __str__(self):
        return f"{self.content}"