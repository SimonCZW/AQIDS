#!/usr/bin/env python
# -*- coding:utf-8 -*-

import db
import apidetail

def main():
    db.create_engine(user='root', password='123456', database='test')

    testdata={'it1': 'itttttt1', 'it2': 1.5, 'it3': 123}
    table_name = 'TestTable'
    primary_keys = ['it1', 'it2']

    with db.connection():
        apidetail.insert_db(table_name, primary_keys, testdata)

if __name__ == '__main__':
    main()
