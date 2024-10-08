#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao
import os
from typing import Optional, List
from harmo import base_utils
from ruamel.yaml import YAML
from pathlib2 import Path

def get_yaml_data(file_path: str) -> dict:
    '''
    传入yaml文件路径，返回yaml文件内的数据，返回类型为dcit
    :param yaml_file:
    :return:
    '''
    file = base_utils.file_is_exist(file_path)
    yaml = YAML(typ='safe', pure=True)
    if Path(file).suffix in (".yaml",".yml"):
        with open(file,'r',encoding='utf-8-sig') as f:
            file_data = f.read()
        yaml_data = yaml.load(file_data) if yaml.load(file_data) else {}
        return yaml_data
    else:
        raise RuntimeError("The file format must be yaml")

def get_yaml_data_all(catalogue: str,filter: Optional[List[str]]=None) -> dict:
    '''
    获取指定目录下全部yaml文件，并返回yaml文件内的数据，返回类型为dcit
    :param catalogue:目录
    :param filter:需要过滤的文件
    :return:
    '''
    _all_date = {}
    yaml = YAML(typ='safe', pure=True)
    for root, _, files in os.walk(catalogue):
        for file in files:
            if Path(file).suffix in (".yaml",".yml"):
                if filter is not None and file in filter:
                    continue
                _full_path = os.path.join(root, file)
                with open(_full_path,'r',encoding='utf-8-sig') as f:
                    _full_path = f.read()
                    yaml_data = yaml.load(_full_path) if yaml.load(_full_path) else {}
                    _all_date = {**yaml_data,**_all_date}
    return _all_date

def writer_yaml(file: str,data: dict) -> None:
    '''
    写yaml文件
    :param file: 文件路径
    :param data: yaml数据
    :return:
    '''
    yaml = YAML()
    with open(file,"w",encoding="utf-8") as f:
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(data,f)

if __name__ == '__main__':
    pass
    #读取信息
    yamldata = get_yaml_data(file_path='../../data/config.yaml')
    print(yamldata)
    yamldataall = get_yaml_data_all(catalogue='../../data',filter=["_global_map.yaml"])
    print(yamldataall)
    # writer_yaml(file="../template/config/global/te.yaml",data=yamldataall)