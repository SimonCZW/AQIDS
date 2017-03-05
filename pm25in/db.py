#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import functools
import MySQLdb

# global use engine
engine = None

def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    """
    Usage:
        import db
        db.create_engine(user='root', password='password', database='test',
            host='127.0.0.1', port=3306)
    """
    global engine
    if engine is not None:
        raise DBError('Engine is already initialized')
    params = dict(user=user, passwd=password, db=database,
                  host=host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', autocommit=False)
    for key, value in defaults.iteritems():
        params[key] = kw.pop(key, value)
    params.update(kw)
    engine = _Engine(MySQLdb.connect(**params))

def connection():
    """
    For multiply operation in one connection.
    Usage:
        create_engine(...)
        with connection():
            select2(...)
            select1(...)
            ...
    """
    return _ConnectionCtx()

def with_connection(func):
    """
    decorate for auto connect and close mysql connect
    """
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)
    return _wrapper

@with_connection
def _update(sql, *args):
    """
    execute sql for insert, delete, create and so on, return effect row count
    """
    global _dbctx
    cursor = None
    sql = sql.replace('?', '%s')
    try:
        cursor = _dbctx.cursor()
        cursor.execute(sql % args)
        update_row_number = cursor.rowcount
        try:
            if _dbctx.transations == 0:
                _dbctx.commit()
            return update_row_number
        except:
            _dbctx.rollback()
            return 0

    # except Exception, e:
        # raise DBError(e)

    finally:
        if cursor:
            cursor.close()

@with_connection
def _select(sql, single=False, *args):
    """
    select sql, if single is not None just return one line.
    """
    global _dbctx
    cursor = None
    sql = sql.replace('?', '%s')

    try:
        cursor = _dbctx.cursor()
        cursor.execute(sql % args)
        # table itemnames
        names = [x[0] for x in cursor.description]
        if single:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names, values)
        else:
            return [Dict(names, values) for values in cursor.fetchall()]

    # except Exception, e:
        # raise Exception(e)

    finally:
        if cursor:
            cursor.close()

def select(sql, *args):
    return _select(sql, False, *args)

def select_one(sql, *args):
    return _select(sql, True, *args)
def has_table(table_name):
    """
    Judge whether had ceated table.
    If table had been created, function return 1 else 0.
    Usage:
        has_table(table_name)
    """
    sql = 'select count(*) from information_schema.TABLES where table_name="?";'
    _result = select_one(sql, table_name)
    # except result format: {'count(*)': number}
    if len(_result) != 1:
        raise Exception('Expect only one column.')
    return _result.values()[0]

def insert(table_name, data):
    """
    Insert datas into table, and success to insert data return 1(row).
    data is dict.
    """
    _keys = ''
    _values = ''
    if has_table(table_name):
        for key, value in data.iteritems():
            #for unicode(chinese data)
            if isinstance(key, unicode):
                # key = key.encode('utf-8')
                _keys = _keys + key + ','
            else:
                _keys = _keys + str(key) + ','
            #for unicode(chinese data)
            if isinstance(value, unicode):
                _values = _values + '"' + value + '"' + ','
            else:
                _values = _values + '"' + str(value) + '"' + ','
        _keys = _keys[:-1]
        _values = _values[:-1]
        _sql = "insert into %s(%s) values(%s)" % (table_name, _keys, _values)
        return _update(_sql)
    else:
        raise Exception('Donnot exists table: %s .' % table_name)

def create_table(table_name, primary_keys, table_items):
    """
    Create table. Primary_keys is a List and table_items is a Dict.
    """
    sql = "create table %s(" % table_name
    for key, value in table_items.iteritems():
        DDL = key + " " + value + " " + "not null, "
        sql = sql + DDL
    sql = sql + "primary key("
    for primary_key in primary_keys:
        sql = sql + primary_key + ', '
    sql = sql.rstrip(', ')
    sql = sql + "))character set utf8 collate utf8_unicode_ci;"
    try:
        _update(sql)
    # table already exists
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print "Error create_table: ", e

class Dict(dict):
    """
    two dict input as new dict's key and value, return this new dict
    """
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for key, value in zip(names, values):
            self[key] = value

class DBError(Exception):
    """
    MySQLdb Error
    """
    def __init__(self, message):
        return message

class _Engine(object):
    """
    store mysqldb connection
    """
    def __init__(self, connect):
        self._connect = connect
    def connect(self):
        return self._connect

class _LasyConnection(object):
    """
    for cursor
    """
    def __init__(self):
        self.connection = None

    def cursor(self):
        # global engine
        if self.connection is None:
            _connection = engine.connect()
            self.connection = _connection
        return self.connection.cursor()

    def cleanup(self):
        if self.connection:
            _connection = self.connection
            self.connection = None
            _connection.close()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()


class _Dbctx(threading.local):
    """
   For thread
    """
    def __init__(self):
        self.connection = None
        self.transations = 0

    def is_not_init(self):
        return self.connection is None

    def is_init(self):
        return self.connection is not None

    def init(self):
        self.connection = _LasyConnection()

    def cursor(self):
        return self.connection.cursor()

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

_dbctx = _Dbctx()
class _ConnectionCtx(object):
    """
    auto connect and close.
    """
    def __enter__(self):
        """ connect """
        global _dbctx
        self.should_clean = False
        if _dbctx.is_not_init():
            _dbctx.init()
            self.should_clean = True
        return self

    def __exit__(self, type, value, trace):
        """ close """
        global _dbctx
        if self.should_clean:
            _dbctx.cleanup()
            self.should_clean = False


if __name__ == '__main__':
    create_engine(user='root', password='123456', database='test')

    # Testing for has_table(), create_table(), get_items()
    # import apidetail
    # with connection():
        # testdata={'it1': 'itttttt1', 'it2': 1.5, 'it3': 123}
        # table_name = 'TestTable'
        # primary_keys = ['it1', 'it2']
        # if not has_table(table_name):
            # table_items = apidetail.get_items(testdata)
            # create_table(table_name, primary_keys, table_items)
            # print "create table"
        # else:
            # print "Table already exists"
        # if has_table(table_name):
            # print insert(table_name, testdata)

    # Testing for _update function
    # sql = """create table Course(
# cid varchar(255) primary key,
# cname varchar(255) not null,
# chours int not null,
# credit float not null,
# precid varchar(255)
# );"""
    # _update(sql)

    # Testing for _select function
    # sql = "select * from Course;"
    # print _select(sql, single=True)
