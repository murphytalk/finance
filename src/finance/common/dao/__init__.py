# -*- coding: utf-8 -*-
from dao.impl import ImplDao
from dao.random import RandomDataDao


class Dao:
    singleton = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not Dao.singleton:
            if len(args) == 1 or args[1] is None:
                Dao.singleton = RandomDataDao()
            else:
                Dao.singleton = ImplDao(args[1])
        return Dao.singleton

    def __getattr__(self, item):
        return getattr(self.singleton, item)

    def __setattr__(self, key, value):
        return setattr(self.singleton, key, value)
