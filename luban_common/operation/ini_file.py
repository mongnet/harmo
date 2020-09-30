#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2018/7/31 17:34
# @Author  : hubiao
# @File    : ini_file.py
import configparser
import os

from pathlib2 import Path

from luban_common.base_utils import file_is_exist


class ManageConfig:
    '''
    配置管理
    '''
    def __init__(self,file_path):
        if Path(file_path).suffix == ".ini":
            self.conf_path = file_is_exist(file_path)
        else:
            raise RuntimeError("The file format must be ini")
        self.config = configparser.RawConfigParser()

    def getConfig(self,section):
        '''
        获取指定节点下的配置
        :param section: 节点名称
        :return: 返回指定节点下的全部配置信息
        '''
        try:
            self.config.read(self.conf_path,encoding='utf-8-sig')
            return self.config[section]
        except BaseException as e:
            print("读取失败！", str(e))

    def getAllConfig(self):
        '''
        获取全部节点配置信息
        :return: 返回全部配置信息
        '''
        try:
            self.config.read(self.conf_path,encoding='utf-8-sig')
            return self.config
        except BaseException as e:
            print("读取失败！", str(e))

    def writeConfig(self,section,key,value):
        '''
        写入配置信息到指定的节点
        :param section: 节点名
        :param key: 配置的key信息
        :param value: 配置的value信息
        :return:
        '''
        try:
            #必须要先读取全部数据，再写入，不然数据会被覆盖
            self.config.read(self.conf_path,encoding='utf-8-sig')
            #判断节点是否存在，不存在时添加节点
            if self.config.has_section(section) is False:
                self.config[section] = {}
            self.config.set(section,key,value)
            with open(self.conf_path,'w',encoding='utf-8-sig') as configfile:
                self.config.write(configfile)
        except BaseException as e:
            print("写入失败！", str(e))

if __name__ == '__main__':
    #读取信息
    cf = ManageConfig(file_path='../../data/intranet.ini')
    # 获取全部配置
    allconf = cf.getAllConfig()
    print(allconf['openapi']["openapiurl"])
    # 获取指定配置
    rf = cf.getConfig('openapi')
    print(rf["openapiurl"])
    # 写入信息
    cf.writeConfig(section='pds',key='cas',value='http://cas.com')

