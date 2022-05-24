from collections import OrderedDict
import inspect

import psycopg2

from exceptions import DeletionFailed, ModelNotFound, MultipleObjectsReturned
from fields import BaseField, ForeignKey
from querysets import  FlatValuesListIterable, ModelIterable, Queryset, ValuesIterable, ValuesListIterable
from settings import DB_SETTINGS


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
        return Queryset(ModelIterable, self.model, cursor, sql, cols)
    
    def create(self, **kwargs):
        cursor = self._get_cursor()
        sql, fields, params = self.model._get_create_sql(**kwargs)
        # print(sql, fields, params)
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
    
    def values(self, *args):
        cursor = self._get_cursor()
        sql, cols = self.model._get_values_sql(*args)
        return Queryset(ValuesIterable, self.model, cursor, sql, list(cols))
    

    def values_list(self, *args, **kwargs):
        cursor = self._get_cursor()
        sql, cols = self.model._get_values_sql(*args)
        iterable = FlatValuesListIterable if kwargs.get('flat') else ValuesListIterable
        return Queryset(iterable, self.model, cursor, sql, list(cols))
    
    def where(self, **kwargs):
        cursor = self._get_cursor()
        sql, cols, params = self.model._get_filter_sql(**kwargs)
        return Queryset(ModelIterable, self.model, cursor, sql, cols, params=params)


class MetaModel(type):
    """Metaclass for all models."""

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
    """ Base Model Class """
    def __init__(self, **kwargs):
        self._state = {
            "id": None
        }
        for key, value in kwargs.items():
            self._state[key] = value

        # set defaults
        for name, column_type in inspect.getmembers(type(self)):
            # prevent foreign key overwrites
            if isinstance(column_type, BaseField) and name not in self._state and f"{name}_id" not in self._state:
                if isinstance(column_type, ForeignKey):
                    if '_id' not in name:
                        name = f"{name}_id"
                val = getattr(column_type, 'default')
                self._state[name] = val
    
    def __getattribute__(self, key):
        # prevent recursion
        _state = super().__getattribute__("_state")
        if key in _state:
            return _state[key]
        return super().__getattribute__(key)
    
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in self._state:
            self._state[name] = value

    # helper methods

    @classmethod
    def _get_create_sql(cls, **kwargs):
        sql = "INSERT INTO {table_name}s_{table_name} ({column_names}) VALUES ({placeholders}) RETURNING id;"
        table_name = cls.__name__.lower()
        cols = []
        placeholders = []
        values = []
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, BaseField):
                if isinstance(column_type, ForeignKey):
                    if '_id' not in name:
                        name = f"{name}_id"
                    cols.append(name)
                else:
                    cols.append(name)
                placeholders.append('%s')
                # append instances default value if name not present
                values.append(kwargs.get(name, getattr(column_type, 'default')))

        final_sql = sql.format(
            table_name=table_name,
            column_names=", ".join(cols), 
            placeholders=", ".join(placeholders)
            )
        return final_sql, cols, values
    
    @classmethod
    def _create_table_sql(cls):
        sql = "CREATE TABLE IF NOT EXISTS {table_name}s_{table_name} ({columns});"
        table_name = cls.__name__.lower()
        columns = ['id SERIAL PRIMARY KEY']
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, BaseField):
                if isinstance(column_type, ForeignKey):
                    columns.append(f'{column_type.get_fk_text(name)}')
                else:
                    columns.append(f'{name} {column_type.get_sql_text}')
        final_sql = sql.format(
            table_name=table_name, 
            columns=", ".join(columns))
        return final_sql

    def _get_delete_sql(self):
        sql = "DELETE from {table_name}s_{table_name} WHERE id = %s"
        cls = self.__class__
        values = [getattr(self, 'id')]
        final_sql = sql.format(table_name=cls.__name__.lower())
        return final_sql, values

    @classmethod
    def _get_filter_sql(cls, **kwargs):
        sql = """
        SELECT {fields} FROM {table_name}s_{table_name}
        WHERE {criteria};
        """ 
        table_name = cls.__name__.lower()
        
        fields = []
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, BaseField):
                if isinstance(column_type, ForeignKey):
                        fields.append(f'{name}_id')
                else:
                    fields.append(name)
        
        if 'id' not in fields:
            fields.insert(0, 'id')

        cols = OrderedDict(**kwargs)
        criteria = [name for name in cols.keys()]
        values = [val for  val in cols.values()]

        final_sql = sql.format(
            fields = ", ".join(fields),
            table_name=table_name,
            criteria=f"{'=%s AND '.join(criteria)}=%s"
        )
    
        return final_sql, fields, values


    def _get_insert_sql(self):
        sql = "INSERT INTO {table_name}s_{table_name} ({column_names}) VALUES ({placeholders}) RETURNING id;"
        cls = self.__class__
        cols = []
        values = []
        placeholders = []
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, BaseField):
                if isinstance(column_type, ForeignKey):
                        cols.append(f'{name}_id')
                        values.append(getattr(self, f"{name}_id"))
                else:
                    cols.append(name)
                    values.append(getattr(self, name))
                placeholders.append('%s')
        
        final_sql = sql.format(
            table_name=cls.__name__.lower(),
            column_names=", ".join(cols),
            placeholders=", ".join(placeholders)
            )
        return final_sql, values
    
    @classmethod
    def _get_select_all_sql(cls):
        sql = "SELECT {columns} FROM {table_name}s_{table_name};"
        table_name = cls.__name__.lower()
        cols = ['id']
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, BaseField):
                if isinstance(column_type, ForeignKey):
                    name = f"{name}_id"
                cols.append(name)
        
        final_sql = sql.format(columns=", ".join(cols), table_name=table_name)
        return final_sql, cols

    @classmethod
    def _get_single_row_sql(cls, **kwargs):
        sql = """
        SELECT {fields} FROM {table_name}s_{table_name}
        WHERE {criteria};
        """ 
        table_name = cls.__name__.lower()
        fields = []
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, BaseField):
                if isinstance(column_type, ForeignKey):
                        fields.append(f'{name}_id')
                else:
                    fields.append(name)
                    
        if 'id' not in fields:
            fields.insert(0, 'id')
        cols = OrderedDict(**kwargs)
        criteria = [name for name in cols.keys()]
        values = [val for  val in cols.values()]
        final_sql = sql.format(
            fields = ", ".join(fields),
            table_name=table_name,
            criteria=f"{'=%s AND '.join(criteria)}=%s"
        )
    
        return final_sql, fields, values

    @classmethod
    def _get_values_sql(cls, *args):
        sql = "SELECT {columns} FROM {table_name}s_{table_name};"
        table_name = cls.__name__.lower()
        final_sql = sql.format(columns=", ".join(args), table_name=table_name)
        return final_sql, args
    

    def _get_update_sql(self):
        sql = "UPDATE {table_name}s_{table_name} SET {fields} WHERE id = %s"
        cls = self.__class__
        cols = []
        values = []
        for name, column_type in inspect.getmembers(cls):
            if isinstance(column_type, BaseField):
                if isinstance(column_type, ForeignKey):
                    name = f"{name}_id"
                cols.append(name)
                values.append(getattr(self, name))
        
        values.append(getattr(self, 'id'))

        final_sql = sql.format(
            table_name=cls.__name__.lower(),
            fields=", ".join([f"{col} = %s" for col in cols])
            )

        return final_sql, values
    
    # public methods
    
    def delete(self):
        """Delete instance in db"""
        try:
            cls = type(self)
            db = cls._db
            cursor = db.cursor()
            sql, params = self._get_delete_sql()
            cursor.execute(sql, params)
            db.commit()
        except Exception as e:
            raise DeletionFailed(e)
                
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
