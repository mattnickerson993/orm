from collections import OrderedDict
import inspect
import psycopg2

from settings import DB_SETTINGS
from exceptions import ModelNotFound, MultipleObjectsReturned
from helpers import Column

# class Database:
#     def __init__(self):
#         self.conn = psycopg2.connect(
#             dbname=DB_SETTINGS.get('DB_NAME'),
#             user=DB_SETTINGS.get('DB_USER'),
#             password=DB_SETTINGS.get('DB_PASS'),
#             host=DB_SETTINGS.get('DB_HOST')
#         )


#     def get(self,  **kwargs):
#         sql, fields, params = model._get_single_row_sql(**kwargs)
#         cur = self.conn.cursor()
#         cur.execute(sql, params)
#         res = cur.fetchall()
#         num_rows = len(res)

#         if num_rows > 1:
#             raise MultipleObjectsReturned(f"Call to model manager expected 1 object, call returned {num_rows}!")
#         elif not num_rows:
#             raise ModelNotFound('No objects returned from query')
        
#         instance = model()
#         for field, val in zip(fields, res[0]):
#             setattr(instance, field, val)
#         return instance


# class Model():
#     def __init__(self, **kwargs):
#         self._data = {
#             "id": None
#         }
#         self.db = Database()
#         for key, value in kwargs.items():
#             self._data[key] = value

#     def __getattribute__(self, key):
#         _data = super().__getattribute__("_data")
#         if key in _data:
#             return _data[key]
#         return super().__getattribute__(key)
    
#     def __setattr__(self, name, value):
#         super().__setattr__(name, value)
#         if name in self._data:
#             self._data[name] = value
    
#     @classmethod
#     def _get_select_all_sql(cls):
#         SELECT_ALL_SQL = "SELECT {columns} FROM {table_name}s_{table_name};"
#         table_name = cls.__name__.lower()
#         cols = ['id']
#         for name, column_type in inspect.getmembers(cls):
#             if isinstance(column_type, Column):
#                 cols.append(name)
        
#         sql = SELECT_ALL_SQL.format(columns=", ".join(cols), table_name=table_name)
#         return sql, cols



# class Column:
#     def __init__(self, column_type):
#         self.type = column_type
    
#     @property
#     def sql_type(self):
#         SQL_TYPE_MAPPER = {
#             int: "INTEGER",
#             float: "REAL",
#             str: "VARCHAR",
#             bytes: "BLOB",
#             bool: "INTEGER"
#         }
#         return SQL_TYPE_MAPPER[self.type]


# if __name__ == '__main__':
#     model = Model()
#     print(model.db.conn)


class BaseManager:

    connection = None

    @classmethod
    def set_connection(cls, db_settings):
        connection = psycopg2.connect(
            dbname=db_settings.get('DB_NAME'),
            user=db_settings.get('DB_USER'),
            password=db_settings.get('DB_PASS'),
            host=db_settings.get('DB_HOST')
        )
        cls.connection = connection
        return cls
    
    @classmethod
    def _commit(cls):
        cls.connection.commit()

    @classmethod
    def _get_cursor(cls):
        return cls.connection.cursor()

    @classmethod
    def _execute_query(cls, query, params=None):
        cursor = cls._get_cursor()
        cursor.execute(query, params)


    def __init__(self, model):
        self.model = model
    

    def all(self):
        cursor = self._get_cursor()
        sql, cols = self.model._get_select_all_sql()
        cursor.execute(sql)
        res = []
        for row in cursor.fetchall():
            instance = self.model()
            for field, value in zip(cols, row):
                setattr(instance, field, value)
            res.append(instance)          
        return res
    

    def get(self, **kwargs):
        cursor = self._get_cursor()
        sql, fields, params = self.model._get_single_row_sql(**kwargs)
        cursor.execute(sql, params)
        res = cursor.fetchall()
        num_rows = len(res)

        if num_rows > 1:
            raise MultipleObjectsReturned(f"Call to model manager expected 1 object, call returned {num_rows}!")
        elif not num_rows:
            raise ModelNotFound('No objects returned from query')
        
        instance = self.model()
        for field, val in zip(fields, res[0]):
            setattr(instance, field, val)
        return instance

    def save(self, instance):
        cursor = self._get_cursor()
        sql, vals = instance._get_insert_sql()
        cursor.execute(sql, vals)
        res = cursor.fetchone()
        instance._state['id'] = res[0]
        self._commit()
        return instance



class MetaModel(type):
    manager_class = BaseManager.set_connection(DB_SETTINGS)

    def _get_manager(cls):
        return cls.manager_class(model=cls)
    
    @property
    def objects(cls):
        return cls._get_manager()


class Model(metaclass=MetaModel):
    _table_name = ""

    def __init__(self, **kwargs):
        self._state = {
            "id": None
        }
        for key, value in kwargs.items():
            self._state[key] = value
    
    def __getattribute__(self, key):
        _state = super().__getattribute__("_state")
        if key in _state:
            return _state[key]
        return super().__getattribute__(key)
    
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in self._state:
            self._state[name] = value

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

class Message(Model):

    _table_name = 'message'
        
    content = Column(str)

    def __str__(self):
        return f"{self.content}"




if __name__ == "__main__":
    print(Message.objects)
    msgs = Message.objects.all()
    for msg in msgs:
        print(msg.id)
        print(msg.content)

    # msg = Message.objects.get(content='individual message')
    # print(msg)
    # print(msg.id)
    # print(msg.content)

    # msg = Message.objects.get(id=4)
    # print(msg)
    # print(msg.id)
    # print(msg.content)

    # my_msg = Message(content='newest content')
    # msg = Message.objects.save(my_msg)
    # print(msg)
    # print(msg.id)
    # print(msg.content)