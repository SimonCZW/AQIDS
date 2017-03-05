#!/usr/bin/env python
# -*- coding: utf-8 -*-

import db

def main():
    db.create_engine(user='root', password='123456', database='test')
    # sql = 'select * from GuangzhouAverage;'
    # print db.select(sql)
    # sql = 'select * from A;'
    # print db.select(sql)
    # data = {'s': u'\u4e8c'}
    a = u'\u4e8c'
    sql = 'insert into A values("' + a + '");'
    print sql
    db._update(sql)

if __name__ == '__main__':
    main()
