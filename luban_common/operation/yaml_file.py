#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao
import os

import ruamel.yaml
import yaml

from luban_common.base_utils import file_is_exist
from pathlib2 import Path

def get_yaml_data(file_path):
    '''
    传入yaml文件路径，返回yaml文件内的数据，返回类型为dcit
    :param yaml_file:
    :return:
    '''
    file = file_is_exist(file_path)
    if Path(file).suffix in (".yaml",".yml"):
        with open(file,'r',encoding='utf-8-sig') as f:
            file_data = f.read()
        return yaml.safe_load(file_data)
    else:
        raise RuntimeError("The file format must be yaml")

def get_yaml_data_all(catalogue) -> dict:
    '''
    获取目录下全部，返回yaml文件内的数据，返回类型为dcit
    :param catalogue:目录
    :return:
    '''
    _conf_date = {}
    for root, _, files in os.walk(catalogue):
        for file in files:
            if Path(file).suffix in (".yaml",".yml"):
                _full_path = os.path.join(root, file)
                with open(_full_path,'r',encoding='utf-8-sig') as f:
                    _full_path = f.read()
                    _conf_date = {**_conf_date,**yaml.safe_load(_full_path)}
    return _conf_date

def writer_yaml(file,data:dict):
    '''
    写yaml文件
    :param file: 文件路径
    :param data: yaml数据
    :return:
    '''
    with open(file,"w",encoding="utf-8") as f:
        writer = ruamel.yaml.YAML()
        writer.indent(mapping=2, sequence=4, offset=2)
        writer.dump(data,f)

if __name__ == '__main__':
    #读取信息
    # yamldata = get_yaml_data(file_path='../../data/config.yaml')
    # print(yamldata)
    yamldataall = get_yaml_data_all(catalogue='../template/config/global')
    print(yamldataall)
    writer_yaml(file="../template/config/global/te.yaml",data=yamldataall)