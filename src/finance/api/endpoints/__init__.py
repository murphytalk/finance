from flask import current_app
from finance.common.report import Dao


def run_func_against_dao(func):
    dao = Dao(current_app.config['DATABASE'])
    dao.connect()
    ret = func(dao)
    dao.close()
    return ret

