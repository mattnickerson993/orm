from collections import OrderedDict
import inspect
import psycopg2

from settings import DB_SETTINGS
from exceptions import ModelNotFound, MultipleObjectsReturned


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=DB_SETTINGS.get('DB_NAME'),
            user=DB_SETTINGS.get('DB_USER'),
            password=DB_SETTINGS.get('DB_PASS'),
            host=DB_SETTINGS.get('DB_HOST')
        )

    
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


class Model():
    def __init__(self, **kwargs):
        self._data = {
            "id": None
        }
        self.db = Database()
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
    def _get_select_all_sql(cls):
        SELECT_ALL_SQL = "SELECT {columns} FROM {table_name}s_{table_name};"
        table_name = cls.__name__.lower()
        cols = ['id']
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, Column):
                cols.append(name)
        
        sql = SELECT_ALL_SQL.format(columns=", ".join(cols), table_name=table_name)
        return sql, cols



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


if __name__ == '__main__':
    model = Model()
    print(model.db.conn)
    