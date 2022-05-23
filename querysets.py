from collections import OrderedDict

class EmptyObj():
    pass

class Queryset():
    
    def __init__(self, iterable_class, model, cursor, sql, fields, params=None, flat=None):
        self._result_cache = None
        self._iterable_class = iterable_class
        self.model = model
        self.cursor = cursor
        self.sql = sql
        self.fields = fields
        self.params = params
        self.flat = flat
    
    def _chain(self):
        """
        Return copy of current query that can be modified through queryset chaining
        """
        obj = self._clone()
        return obj
    
    def _clone(self):
        obj = EmptyObj()
        obj.__class__ = self.__class__
        obj.__dict__ = self.__dict__.copy()
        obj.model = self.model
        obj.sql = str(self.sql)
        obj.fields = self.fields.copy()
        obj.params = self.params.copy() if self.params is not None else None
        return obj
    
    def count(self):
        self._fetch_all()
        return len(self._result_cache)

    def __getitem__(self, key):
        self._fetch_all()
        return self._result_cache[key]

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self._iterable_class(self))

    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)
    
    def __len__(self):
        self._fetch_all()
        return len(self._result_cache)
    
    def where(self, **kwargs):
        obj = self._chain()
        obj.sql, obj.params = self._filter_fields(obj.sql, **kwargs)
        return obj

    def values_list(self, *args, flat=False):
        obj = self._chain()
        obj._iterable_class = ValuesListIterable if flat == False else FlatValuesListIterable
        obj.sql,  obj.fields = self._format_values(obj.sql, *args)
        return obj

    
    def values(self, *args):
        obj = self._chain()
        obj._iterable_class = ValuesIterable
        obj.sql,  obj.fields = self._format_values(obj.sql, *args)
        return obj
    
    def _format_values(self, sql, *args):
        _, old_sql = sql.split('FROM')
        
        SQL = "SELECT {columns} FROM {old_sql};"
        FINAL_SQL = SQL.format(
            columns = ", ".join(args),
            old_sql = old_sql
        )
        return FINAL_SQL, list(args)

    def order_by(self, *fields):
        """Return a new QuerySet instance with the ordering changed."""
        obj = self._chain()
        obj.sql = self.order_fields(obj.sql, *fields)
        return obj
    
    def _filter_fields(self, sql, **kwargs):
        sql = sql.replace(';', '')
        SQL = "{orig_sql} WHERE {conditions};"
        cols = OrderedDict(**kwargs)
        criteria = [name for name in cols.keys()]
        values = [val for  val in cols.values()]
        FINAL_SQL = SQL.format(
            orig_sql=sql,
            conditions=f"{'=%s AND '.join(criteria)}=%s"
        )
    
        return FINAL_SQL, values

    def order_fields(self, sql, *fields):
        sql = sql.replace(';', '')
        SQL = "{orig_sql} ORDER BY {ordered_fields};"
        ordered_fields = [f"{field[1:]} DESC" if field.startswith('-') else f"{field}" for field in fields]
        return SQL.format(orig_sql=sql, ordered_fields=", ".join(ordered_fields))

    def __repr__(self):
        data = list(self[:5])
        if len(data) > 5:
            data[-1] = "...(remaining elements truncated)..."
        return "<%s %r>" % (self.__class__.__name__, data)



class ModelIterable():
    
    def __init__(self, queryset):
        self.queryset = queryset
        

    def __iter__(self):
        self.queryset.cursor.execute(self.queryset.sql, self.queryset.params)
        for row in self.queryset.cursor.fetchall():
            instance = self.queryset.model()
            for field, value in zip(self.queryset.fields, row):
                setattr(instance, field, value)
            yield instance


class ValuesIterable():
    def __init__(self, queryset):
        self.queryset = queryset

    def __iter__(self):
        self.queryset.cursor.execute(self.queryset.sql, self.queryset.params)
        fields = self.queryset.fields
        indexes = range(len(fields))
        for row in self.queryset.cursor.fetchall():
            yield {fields[i]: row[i] for i in indexes}

class ValuesListIterable():
    def __init__(self, queryset):
        self.queryset = queryset
    
    def __iter__(self):
        self.queryset.cursor.execute(self.queryset.sql, self.queryset.params)
        for row in self.queryset.cursor.fetchall():
            yield row


class FlatValuesListIterable():
    """
    Iterable returned by QuerySet.values_list(flat=True) that yields single
    values.
    """
    def __init__(self, queryset):
        self.queryset = queryset
        
    def __iter__(self):
        self.queryset.cursor.execute(self.queryset.sql, self.queryset.params)
        for row in self.queryset.cursor.fetchall():
            yield row[0]