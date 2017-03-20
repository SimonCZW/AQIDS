#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2

class GetJsonApiBase(object):
    def __init__(self, token=None):
        """
        Set token and init database.
        Usage:
            >>> token = 'xxxx'
            >>> GetJsonApiBase(token)
        """
        self.token = token

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
        if self.token is not None:
            params = {'token': self.token}
        else:
            params = {}

        if other_params is not None:
            params.update(other_params)
        url_params = urllib.urlencode(params)

        if url_params != '':
            url = api_url + '?' + url_params
        else:
            url = api_url

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
