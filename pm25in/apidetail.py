#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import datetime

import db

def get_items(data):
    """
    return table items from data for create table.
    """
    _table_items = {}
    for key, value in data.iteritems():
        if isinstance(value, int):
            _table_items[key] = "int"
        elif isinstance(value, float):
            _table_items[key] = "float"
        # elif isinstance(value, str):
        else:
            # include time_point
            _table_items[key] = "varchar(255)"
    return _table_items

def insert_db(table_name, primary_keys, data):
    """
    Insert data in to table.

    First, judging whether had created table, if not create it(having primary).
    Second, it will get the type of data items for creating table.//get_items()
    After creating table, insert data into table.

    Usage:
        with db.connection():
            apidetail.insert_db(table_name, primary_keys, data)

        Using "with db.connection():":
        Because insert_db do multiply action in one MySQLdb connection.
    """
    # has no table and create it.
    if not db.has_table(table_name):
        table_items = get_items(data)

        try:
            db.create_table(table_name, primary_keys, table_items)
        except Exception, e:
            print  'Created table failed. Reason:', e

    try:
        db.insert(table_name, data)
    except Exception, e:
        print 'Inserted data into %s failed.(data: %s)' % (table_name, data)
        print e


def main():
    # all datas aqi
    api_url = "http://www.pm25.in/api/querys/aqi_details.json"
    city = "guangzhou"
    token = "5j1znBVAsnSf5xQyNQyq"
    now_time = datetime.datetime.now().strftime("%Y%m%d%H")

    values = {'city': city, 'token': token}
    datas = urllib.urlencode(values)
    url = api_url + '?' + datas

    # connect to database
    db.create_engine(user='root', password='123456', database='test')

    try:
        api_details = urllib2.urlopen(url)
        all_datas = json.load(api_details)

        # print all_datas
        for data in datas:
            # example: 2017-03-01T16:00:00Z -> 2017030216(year-mon-day-hour)
            timestamp = datetime.datetime.strptime(
                data['time_point'],"%Y-%m-%fT%H:%M:%SZ").strftime("%Y%m%d%H")
            data['time_point'] = timestamp

            # is newest data?
            if now_time > timestamp:
                print "Not the newest data: ", data
                datas.remove(data)
            # newest data, insert to db
            else:
                # last data: average city data
                if data['station_code'] is None and data['position_name'] is None:
                    data.pop('station_code')
                    data.pop('position_name')

                    table_name = city.capitalize() + "Average"
                    primary_keys = ['time_point']
                    with db.connection():
                        insert_db(table_name, primary_keys, data)
                # station data
                else:
                    primary_keys = ['station_code']
                    table_name = city.capitalize() + timestamp
                    with db.connection():
                        insert_db(table_name, primary_keys, data)

    except:
        print "not data from %s", url


if __name__ == '__main__':
    main()

    # Testing for insert_db function...
    # db.create_engine(user='root', password='123456', database='test')
    # testdata={'it1': 'itttttt1', 'it2': 1.5, 'it3': 123}
    # table_name = 'TestTable'
    # primary_keys = ['it1', 'it2']
    # with db.connection():
        # insert_db(table_name, primary_keys, testdata)
