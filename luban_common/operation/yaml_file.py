#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao

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
    if Path(file).suffix == ".yaml":
        with open(file,'r',encoding='utf-8-sig') as f:
            file_data = f.read()
        return yaml.safe_load(file_data)
    else:
        raise RuntimeError("The file format must be yaml")

if __name__ == '__main__':
    #读取信息
    yamldata = get_yaml_data(file_path='../../data/config.yaml')
    print(yamldata)