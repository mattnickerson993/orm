class EmptyObj():
    pass

class Queryset():
    
    def __init__(self, model, cursor, sql, fields, params=None):
        self._result_cache = None
        self.model = model
        self.cursor = cursor
        self.sql = sql
        self.fields = fields
        self.params = params
        self._iterable_class = ModelIterable
    
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
    
    
    def order_by(self, *fields):
        """Return a new QuerySet instance with the ordering changed."""
        obj = self._chain()
        obj.sql = self.order_fields(obj.sql, *fields)
        print(obj.sql)
        return obj
    
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