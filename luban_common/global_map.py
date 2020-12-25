#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TIME    : 2020/10/20 18:07
# Author  : hubiao
# File    : global_map.py

import json

class Global_Map:
    '''
    全局变量
    '''
    __map = {}

    @classmethod
    def set(self, key, value):
        if(isinstance(value,dict)):
            value = json.dumps(value)
        self.__map[key] = value

    @classmethod
    def sets(self, **keys):
        try:
            for key_, value_ in keys.items():
                self.__map[key_] = str(value_)
        except BaseException as msg:
            raise msg

    @classmethod
    def del_key(self, key):
        try:
            del self.__map[key]
            return self.__map
        except KeyError:
            print()

    @classmethod
    def get(self,*args):
        try:
            dic = {}
            for key in args:
                if len(args)==1:
                    dic = self.__map[key]
                elif len(args)==1 and args[0]=='all':
                    dic = self.__map
                else:
                    dic[key]=self.__map[key]
            return dic
        except KeyError:
            return 'Null_'

if __name__ == '__main__':
    gl = Global_Map()
