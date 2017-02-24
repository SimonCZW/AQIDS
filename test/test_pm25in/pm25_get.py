#!/usr/bin/env python

import requests

r = requests.get('http://www.pm25.in/api/querys/pm2_5.json?city=zhuhai&token=5j1znBVAsnSf5xQyNQyq')

print r.text
