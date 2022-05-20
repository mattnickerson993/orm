from datetime import datetime
import random
from unittest.util import _MAX_LENGTH

from exceptions import MaxLengthRequired

class Column:
    def __init__(self, column_type):
        self.field_type = column_type
    
    @property
    def sql_type(self):
        SQL_TYPE_MAPPER = {
            IntegerField: "integer",
            FloatField: "double precision",
            CharField: "varchar(%(max_length)s)",
            BooleanField: "boolean",
            DateTimeField: "timestamp with time zone",
            TextField: "text"

        }
        print('self', self.field_type)
        return SQL_TYPE_MAPPER[self.field_type]
    

class BaseField():
    nullable = False
    blank = False
    pk = False
    fk = False

class IntegerField(BaseField):
    def __init__(self, nullable=False, default=None):
        self.nullable = nullable
        self.default = default
    
    @property
    def get_sql_text(self):
        BASE_SQL = "integer{nullable}"
        nullable = "" if self.nullable else " NOT NULL"
        return BASE_SQL.format(nullable=nullable)

class FloatField(BaseField):
    def __init__(self, nullable=False, default=None):
        self.nullable = nullable
        self.default = default
    
    @property
    def get_sql_text(self):
        BASE_SQL = "double precision{nullable}"
        nullable = "" if self.nullable else " NOT NULL"
        return BASE_SQL.format(nullable=nullable)

class CharField(BaseField):

    def __init__(self, max_length=255, nullable=False, default=None):
        self.max_length = max_length
        self.nullable = nullable
        self.default = default
    
    @property
    def get_sql_text(self):
        BASE_SQL = "varchar({max_length}){nullable}"
        nullable = "" if self.nullable else " NOT NULL"
        return BASE_SQL.format(max_length=self.max_length, nullable=nullable)
    

class DateTimeField(BaseField):

    def __init__(self, nullable=False, default=None):
        self.nullable = nullable
        self.default = default
    
    @property
    def get_sql_text(self):
        BASE_SQL = "timestamp with time zone{nullable}"
        nullable = "" if self.nullable else " NOT NULL"
        return BASE_SQL.format(nullable=nullable)

class BooleanField(BaseField):
    def __init__(self, nullable=False, default=None):
        self.nullable = nullable
        self.default = default
    
    @property
    def get_sql_text(self):
        BASE_SQL = "boolean{nullable}"
        nullable = "" if self.nullable else " NOT NULL"
        return BASE_SQL.format(nullable=nullable)

    @property
    def get_default_value(self):
        return self.default



class ForeignKey(BaseField):

    def __init__(self, model, nullable=False, default=None, on_delete=None):
        self.model = model
        self.nullable = nullable
        self.default = default
        self.on_delete = on_delete

    def get_fk_text(self, name):
        BASE_SQL = "{name}_id BIGINT{nullable} REFERENCES {name}s_{name}(id) ON DELETE {on_delete}"
        nullable = "" if self.nullable else " NOT NULL"
        return BASE_SQL.format(name = name, nullable=nullable, on_delete=self.on_delete)

    @property
    def get_default_value(self):
        return self.default

class TextField(BaseField):
    def __init__(self, nullable=False, default=None):
        self.nullable = nullable
        self.default = default
    
    @property
    def get_sql_text(self):
        BASE_SQL = "text{nullable}"
        nullable = "" if self.nullable else " NOT NULL"
        return BASE_SQL.format(nullable=nullable)
