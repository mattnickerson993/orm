

class Queryset():
    
    def __init__(self, model, cursor, sql, fields, params=None):
        self._result_cache = None
        self.model = model
        self.cursor = cursor
        self.sql = sql
        self.fields = fields
        self.params = params
        self._iterable_class = ModelIterable

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self._iterable_class(self))

    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)



class ModelIterable():
    
    def __init__(self, queryset):
        self.queryset = queryset
        

    def __iter__(self):
        self.queryset.cursor.execute(self.sql)
        for row in self.queryset.cursor.fetchall():
            yield row
        # fetch results here
        # ie yield obj