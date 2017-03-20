#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2

class GetJsonApiBase(object):
    def __init__(self, token=None): #**database)
        """
        Set token and init database.
        Usage:
            >>> database = dict(user='root', password='123456', database='test')
            >>> token = 'xxxx'
            >>> GetJsonApiBase(token, **database)
        """
        self.token = token
        # db.create_engine(**database)

    def get_api_base(self, api_url, other_params=None,
                      headers=None, data=None, json_format=True):
        """
        Base api request function, Return json type data from API.
        Params is a dict for url params.

        For example:
            api_url: http://api.com
            token: xxxxxxx
            params: {'city': 'guangzhou', 'station': 'no'}
            And the request url:
                http://api.com?token=xxxxxxx&city=guangzhou&station=no
            headers: http request header
            data: post request data
            json_format: default return data format is json
        """
        params = {'token': self.token}
        if other_params is not None:
            params.update(other_params)
        url_params = urllib.urlencode(params)
        url = api_url + '?' + url_params
        req = urllib2.Request(url, headers)
        if data:
            req.add_data(data)
        try:
            # req = urllib2.urlopen(url)
            response = urllib2.urlopen(req)
            if json_format is True:
                return json.load(response)
            else:
                return response.read()
        except Exception, e:
            print "Request %s error." % url,
            print e
