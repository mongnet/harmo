#!/usr/bin/python3
# -*- coding: utf-8 -*-
# TIME    : 2020/10/20 18:07
# Author  : hubiao
# File    : global_map.py

import copy

class Global_Map:
    '''
    全局变量
    '''
    map = {}

    @classmethod
    def set(self, key:str, value:[str,int,list,dict,bool]):
        '''
        添加指定变量到全局变量
        :param key: 变量名
        :param value: 变量值
        :return:
        '''
        try:
            self.map[key] = copy.deepcopy(value)
        except BaseException as msg:
            raise msg

    @classmethod
    def sets(self, dict_kwargs: dict):
        '''
        添加多个指定变量到全局变量
        :param dict_kwargs: 变量字典
        :return:
        '''
        try:
            if isinstance(dict_kwargs, dict):
                for key, value in dict_kwargs.items():
                    self.map[key] = copy.deepcopy(value)
        except BaseException as msg:
            raise msg

    @classmethod
    def del_key(self, key: str):
        '''
        删除指定的全局变量
        :param key:
        :return:
        '''
        try:
            del self.map[key]
            return
        except:
            return

    @classmethod
    def get(self,*args):
        '''
        获取指定变量
        :param args: 需要获取的变量名
        :return: 当只有一个变量且名称为’all’ 或 没有args参数时，返回全部变量; 当获取多个变量时，只返回存在的变量
        '''
        dic = {}
        if (len(args)==1 and args[0]=='all') or len(args)==0:
            dic = self.map
        elif len(args) == 1:
            try:
                return self.map[args[0]]
            except:
                pass
        else:
            for key in args:
                try:
                    dic[key]=self.map[key]
                except:
                    pass
        if dic:
            return dic
        else:
            return None

if __name__ == '__main__':
    pass

