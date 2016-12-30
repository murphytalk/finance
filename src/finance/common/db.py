# -*- coding: utf-8 -*-
import os


def get_sql_statements():
    sql = []
    sqlfile = os.path.dirname(os.path.realpath(__file__)) + "/db.sql"
    # filter empty and comment lines
    lines = list(filter(lambda s: len(s.strip()) > 0 and s[0] != '-', open(sqlfile).readlines()))
    count = len(lines)
    i = last = 0
    while i < count:
        if ';' in lines[i]:
            sql.append(''.join(lines[last:i + 1]))
            last = i + 1
        i += 1
    for s in sql:
        yield s


if __name__ == "__main__":
    i = 1
    for sql in get_sql_statements():
        print("SQL #%d" % i)
        print(sql)
        i += 1
