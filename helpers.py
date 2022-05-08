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