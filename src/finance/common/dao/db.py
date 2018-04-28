# -*- coding: utf-8 -*-
import os
import sqlite3

SQL_FILE = os.path.dirname(os.path.realpath(__file__)) + "/db.sql"


class Raw:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.c = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def exec(self, sql, parameters=None):
        if parameters:
            self.c.execute(sql, parameters)
        else:
            self.c.execute(sql)
        return self.c.fetchall()

    def exec_many(self, sql, parameters):
        self.c.executemany(sql, parameters)
        return self.c.fetchall()


def get_sql_statements():
    sql = []
    # filter empty and comment lines
    lines = list(filter(lambda s: len(s.strip()) > 0 and s[0] != '-', open(SQL_FILE).readlines()))
    count = len(lines)
    i = last = 0
    while i < count:
        if ';' in lines[i]:
            sql.append(''.join(lines[last:i + 1]))
            last = i + 1
        i += 1
    for s in sql:
        yield s


def get_sql_scripts():
    with open(SQL_FILE) as f:
        return ''.join(f.readlines())


if __name__ == "__main__":
    i = 1
    for sql in get_sql_statements():
        print("SQL #%d" % i)
        print(sql)
        i += 1
