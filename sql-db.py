import sqlite3
import typing
import logging

def pr(sth):
    print(sth)
    return sth

def group(l: list, length=2):
    return [l[i:i+length] for i in range(0, len(l), length)]

class Database:

    def __init__(self, filename='database.db'):
        '''Объект базы данных'''
        self._conn = sqlite3.connect(filename)
        self._cur = self._conn.cursor()
        self._filename = filename

    def create(self, table: str, columns: tuple):
        self._cur.execute(f'''
                          CREATE TABLE IF NOT EXISTS {table}(
                            {', '.join(columns)}
                          )''')
        self._conn.commit()

    def insert(self, table: str, *values):
        self._cur.execute(f'''
                          INSERT INTO {table}
                          VALUES ({('?,'*len(values)).strip(',')})
                          ''',
                         values)
        self._conn.commit()

    def insert_many(self, table: str, rows):
        self._cur.executemany(f'''
                              INSERT INTO {table}
                              VALUES ({('?,'*len(rows[0])).strip(',')})
                              ''',
                             rows)

    def insert_dict(self, table: str, **data: dict):
        self._cur.execute(f'''
                          INSERT INTO {table}({','.join(data)})
                          VALUES ({('?,'*len(data)).strip(',')})
                          ''',
                         tuple(data.values()))
        self._conn.commit()

    def select(self, table: str, where='', columns=None, ):
        if not columns:
            columns = ('*',)
        if where:
            where = 'WHERE ' + where 
        self._cur.execute(f'''
                          SELECT {','.join(columns)}
                          FROM {table}
                          {where}
                          ''')
        return self._cur.fetchall()

    def delete(self, table: str, where=''):
        if where:
            self._cur.execute(f'''
                              DELETE 
                              FROM {table}
                              WHERE {where}
                              ''')
        else:
            self._cur.execute(f'''
                              DELETE 
                              FROM {table}
                              ''')
        self._conn.commit()

    def update(self, table: str, set: str, where: str):
        self._cur.execute(f'''
                          UPDATE {table}
                          SET {set}
                          WHERE {where}
                          ''')
        self._conn.commit()

    def table_info(self, table: str):
        return self._cur.execute(f'''
                                 PRAGMA table_info({table})
                                 ''').fetchall()


    def __iter__(self):
        return (x[0] for x in self._cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())

    def raw(self):
        return {table_name: Table(self, table_name).raw() for table_name in self}

    def __getitem__(self, table):
        return Table(self, table)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._cur.close()
        self._conn.close()

    def __repr__(self):
        return f"Database(filename='{self._filename}')"

class Table:

    def __init__(self, db, name):
        self._db = db
        self._name = name
        self._info = None
        self._pk = None
        self._keys = None
        self._non_pkeys = None

    @property
    def name(self):
        return self._name

    @property
    def info(self):
        if not self._info:
            self._info = self._db.table_info(self.name)
        return self._info

    @property
    def primary_key(self):
        if not self._pk:
            self._pk = max(self.info, key=lambda x: x[-1])[1]
        return self._pk
            
    @property
    def keys(self):
        if not self._keys:
            self._keys = [item[1] for item in self.info]
        return self._keys
            
    @property
    def non_primary_keys(self):
        if not self._non_pkeys:
            self._non_pkeys = self.keys[:]
            self._non_pkeys.remove(self.primary_key)
        return self._non_pkeys

    def create(self, columns: tuple):
        return self._db.create(self.name, columns)
        
    def insert(self, *values):
        return self._db.insert(self.name, *values)

    def insert_many(self, rows):
        return self._db.insert_many(self.name, rows)

    def insert_dict(self, **data):
        return self._db.insert_dict(self.name, **data)
        
    def select(self, where='', columns=None):
        return self._db.select(self.name, where, columns)
        
    def delete(self, where=''):
        return self._db.delete(self.name, where)

    def update(self, set: str, where: str):
        return self._db.update(self.name, set, where)

    def raw(self):
        return [dict(zip(self.keys, v)) for v in self.select()]

    def append(self, row):
        return self.insert_dict(**dict(zip(self.non_primary_keys, row)))

    def __getitem__(self, key):
        if isinstance(key, tuple):
            values = self.select(','.join('%s=%r'%pair for pair in group(key)))
            items = [dict(zip(self.keys, v)) for v in values]
        else:
            values = self.select(f"{self.primary_key}={repr(key)}")[0]
            items = dict(zip(self.keys, values))
        return items
         
    def __setitem__(self, key, value):
        try:
            if isinstance(key, tuple):
                _where = ','.join('%s=%r'%pair for pair in group(key))
            else:
                _where = f"{self.primary_key}={key}"
            _set = ','.join('%s=%r'%pair for pair in value.items())
            self.update(_set, _where)
        except:
            if isinstance(key, tuple):
                for k,v in value:
                    value[k] = v
            else:
                value[self.primary_key] = key
            self.insert_dict(**value)
            
    def __delitem__(self, key):
        if isinstance(key, tuple):
            _where = ','.join('%s=%r'%pair for pair in group(key))
        else:
            _where = f"{self.primary_key}={repr(key)}"
        self.delete(_where)

    def __len__(self):
        return self.select(columns=('COUNT("*")',))[0][0]

    def __contains__(self, key):
        return bool(self.get(key))

    def __iter__(self):
        return (x[0] for x in self.select(columns=(self.primary_key,)))

    def __repr__(self):
        return f'Table(db={self._db}, name={self.name})'

    def get(self, key, default=None):
        try:
            return self[key]
        except IndexError:
            return default

    def startswtih(self, prefix, key=None):
        return self.select(f'{key or self.primary_key} LIKE {prefix}%')

    def endswith(self, postfix, key=None):
        return self.select(f'{key or self.primary_key} LIKE %{postfix}')
