#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/3/28 20:00
# @Author  : hubiao
import os
from typing import Union, Optional, List
from harmo import base_utils
import json
from pathlib2 import Path

def get_json_data(file_path: str) -> dict:
    '''
    传入json文件路径，返回json文件内的数据，返回类型为dcit
    :param file_path:
    :return: dict
    '''
    file = base_utils.file_is_exist(file_path)
    if Path(file).suffix in (".json"):
        with open(file, 'r', encoding='utf-8-sig') as f:
            json_data = json.load(f)
        return json_data
    else:
        raise TypeError("The file type must be json")

def get_json_data_all(catalogue: str,filter: Optional[List[str]]=None) -> dict:
    '''
    获取指定目录下全部json文件，并返回json文件内的数据，返回类型为dcit
    :param catalogue:目录
    :param filter:需要过滤的文件
    :return: dict
    '''
    _all_date = {}
    for root, _, files in os.walk(catalogue):
        for file in files:
            if Path(file).suffix in (".json"):
                if filter is not None and file in filter:
                    continue
                _full_path = os.path.join(root, file)
                with open(_full_path,'r',encoding='utf-8-sig') as f:
                    _full_path = json.load(f)
                    _all_date = {**_full_path,**_all_date}
    return _all_date

def writer_json(file: str,json_data: Union[dict,list]) -> None:
    '''
    写json文件
    :param file: 文件保存路径
    :param data: json数据
    :return:
    '''
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    if isinstance(json_data, (dict, list)):
        with open(file, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)
    else:
        raise TypeError("The data type must be dict or list")


if __name__ == '__main__':
    pass
    # 读取信息
    # yamldata = get_json_data(file_path='../../data/config.yaml')
    # print(yamldata)
    # print(type(yamldata))
    # yamldataall = get_json_data_all(catalogue='../../data',filter=["swagger_ent_admin.json"])
    # print(yamldataall)
    # print(type(yamldataall))
    # yamldata = {"name": "hubiao"}
    # writer_json(file="../../data/source2.json",json_data=yamldata)