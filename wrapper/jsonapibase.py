#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
from collections import OrderedDict

import db


class GetJsonApiBase(object):
    def __init__(self, token, **database):
        """
        Set token and init database.
        """
        self.token = token
        db.create_engine(**database)

    def _get_api_base(self, api_url, other_params=None):
        """
        Base api request function, Return json type data from API.
        Params is a dict for url params.

        For example:
            api_url: http://api.com
            token: xxxxxxx
            params: {'city': 'guangzhou', 'station': 'no'}
            And the request url:
                http://api.com?token=xxxxxxx&city=guangzhou&station=no
        """
        params = {'token': self.token}
        if other_params is not None:
            params.update(other_params)
        url_params = urllib.urlencode(params)
        url = api_url + '?' + url_params
        try:
            req = urllib2.urlopen(url)
            json_datas = json.load(req)
            return json_datas
        except Exception, e:
            print "Request %s error." % url,
            print e

    def order_data(self, data, orderlist):
        """
        Input a dict, and return Orderdict().Order by orderlist.
        """
        order_data = OrderedDict()
        for item in orderlist:
            order_data[item] = data.get(item)
        return order_data

    def insert_db(self, table_name, primary_keys, data):
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
            table_items = self.get_items(data)

            try:
                db.create_table(table_name, primary_keys, table_items)
            except Exception, e:
                print  'Created table failed. Reason:', e

        try:
            db.insert(table_name, data)
        except Exception, e:
            print 'Inserted data into %s failed.(data: %s)' % (table_name, data)
            print e

    def get_items(self, data):
        """
        return table items from data for create table.
        """
        _table_items = OrderedDict()
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, int):
                _table_items[key] = "int"
            elif isinstance(value, float):
                _table_items[key] = "float"
            else:
                _table_items[key] = "varchar(255)"
        return _table_items
