from collections import OrderedDict
import inspect
import psycopg2

from settings import DB_SETTINGS
from exceptions import ModelNotFound, MultipleObjectsReturned
from helpers import Column


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
    
    def create(self, **kwargs):
        cursor = self._get_cursor()
        sql, fields, params = self.model._get_create_sql(**kwargs)
        cursor.execute(sql, params)
        res = cursor.fetchone()
        new_id = res[0]
        self._commit()
        
        return self.get(id=new_id)
    
    def create_table(self):
        cursor = self._get_cursor()
        sql = self.model._create_table_sql()
        res = cursor.execute(sql)
        self._commit()

    def delete(self, instance):
        cursor = self._get_cursor()
        sql, params = instance._get_delete_sql()
        cursor.execute(sql, params)
        self._commit()

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
    

    def update(self, instance):
        cursor = self._get_cursor()
        sql, vals = instance._get_update_sql()
        cursor.execute(sql, vals)
        self._commit()
        return instance
    
    def where(self, **kwargs):
        cursor = self._get_cursor()
        sql, cols, params = self.model._get_filter_sql(**kwargs)
        cursor.execute(sql, params)
        res = []
        for row in cursor.fetchall():
            instance = self.model()
            for field, value in zip(cols, row):
                setattr(instance, field, value)
            res.append(instance)          
        return res


class MetaModel(type):
    manager_class = BaseManager.set_connection(DB_SETTINGS)

    def _get_manager(cls):
        return cls.manager_class(model=cls)
    
    @property
    def objects(cls):
        return cls._get_manager()
    
    @property
    def _db(cls):
        return cls.manager_class.connection


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
    
    @classmethod
    def _create_table_sql(cls):
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
    
    @classmethod
    def _get_create_sql(cls, **kwargs):
        INSERT_SQL = "INSERT INTO {table_name}s_{table_name} ({column_names}) VALUES ({placeholders}) RETURNING id;"
        table_name = cls.__name__.lower()
        cols = []
        values = []
        placeholders = []
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, Column):
                cols.append(name)
                values.append(kwargs.get(name))
                placeholders.append('%s')

        # cols = OrderedDict(**kwargs)
        # criteria = [name for name in cols.keys()]
        # values = [val for  val in cols.values()]
        cols = ", ".join(cols)
        placeholders = ", ".join(placeholders)
        sql = INSERT_SQL.format(table_name=table_name, column_names=cols, placeholders=placeholders)
        return sql, cols, values

    def _get_delete_sql(self):
        DELETE_SQL = "DELETE from {table_name}s_{table_name} WHERE id = %s"
        cls = self.__class__
        values = [getattr(self, 'id')]
        FINAL_SQL = DELETE_SQL.format(table_name=cls.__name__.lower())
        return FINAL_SQL, values

    @classmethod
    def _get_filter_sql(cls, **kwargs):
        INITIAL_SQL = """
        SELECT {fields} FROM {table_name}s_{table_name}
        WHERE {criteria};
        """ 
        table_name = cls.__name__.lower()
        # get all cls attributes only
        fields = [i[0] for i in inspect.getmembers(cls)
                       if not i[0].startswith('_') and not inspect.isfunction(i[1])
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
                       if not i[0].startswith('_') and not inspect.isfunction(i[1])
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
    
    def delete(self):
        try:
            cls = type(self)
            db = cls._db
            cursor = db.cursor()
            sql, params = self._get_delete_sql()
            cursor.execute(sql, params)
            db.commit()
        except Exception as e:
            return False
    
    def save(self):
        """update instance in db if it exists, otherwise create and update id in instance state"""
        cls = type(self)
        db = cls._db
        cursor = db.cursor()
        id = self._state.get('id')
        if id:
            sql, vals = self._get_update_sql()
            cursor.execute(sql, vals)
        else:
            sql, vals = self._get_insert_sql()
            cursor.execute(sql, vals)
            res = cursor.fetchone()
            self._state['id'] = res[0]
        db.commit()
    
        return self

class Message(Model):

    _table_name = 'message'
        
    content = Column(str)

    def __str__(self):
        return f"{self.content}"


class Job(Model):

    _table_name = 'job'
        
    data = Column(str)

    def __str__(self):
        return f"{self.data}"




if __name__ == "__main__":

     ########## where (filter) ###############
    # print(Message.objects)
    # msgs = Message.objects.where( id=1, content='newest content')
    # for msg in msgs:
    #     print(msg.id)
    #     print(msg.content)
    # msgs = Message.objects.all()
    # for msg in msgs:
    #     print(msg.id)
    #     print(msg.content)


     ########## get ###############
    # msg = Message.objects.get(content='individual message')
    # print(msg)
    # print(msg.id)
    # print(msg.content)
    # msg = Message.objects.get(id=4)
    # print(msg)
    # print(msg.id)
    # print(msg.content)


     ########## create ###############
    # msg = Message.objects.create(
    #     content = 'newly created content againn'
    # )
    # print(msg)
    # print(msg.id)
    # print(msg.content)

    ########## save (create or update) ###############
    # msg = Message(content='content to save')
    # msg.save()
    # print(msg.id)
    # print(msg.content)

    # msgs = Message.objects.where(content='content to save')
    # for msg in msgs:
    #     msg.content = 'modified content'
    #     msg.save()

    ########## delete ###############
    # msg = Message.objects.get(id=1)
    # msg.delete()

    ##############create table ################
    Job.objects.create_table()