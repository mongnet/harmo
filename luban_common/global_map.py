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
    map = {}

    @classmethod
    def set(self, key, value):
        try:
            if(isinstance(value,dict)):
                value = json.dumps(value)
            self.map[key] = value
        except BaseException as msg:
            raise msg

    @classmethod
    def sets(self, **keys):
        try:
            for key_, value_ in keys.items():
                self.map[key_] = str(value_)
        except BaseException as msg:
            raise msg

    @classmethod
    def del_key(self, key):
        try:
            del self.map[key]
            return self.map
        except KeyError:
            raise KeyError

    @classmethod
    def get(self,*args):
        try:
            dic = {}
            for key in args:
                if len(args)==1:
                    dic = self.map[key]
                elif len(args)==1 and args[0]=='all':
                    dic = self.map
                else:
                    dic[key]=self.map[key]
            return dic
        except KeyError:
            return 'Null_'

if __name__ == '__main__':
    gl = Global_Map()
