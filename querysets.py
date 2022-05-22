

class Queryset():
    
    def __init__(self, model, cursor, sql, fields, params=None):
        self._result_cache = None
        self.model = model
        self.cursor = cursor
        self.sql = sql
        self.fields = fields
        self.params = params
        self._iterable_class = ModelIterable
    
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
        return
        
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