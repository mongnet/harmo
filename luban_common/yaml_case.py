#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023-9-15 21:25
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : yaml_case.py

from luban_common import base_utils
from luban_common.global_map import Global_Map
from luban_common.operation.yaml_file import get_yaml_data
from luban_common.render_template import rend_template_any
import importlib
import importlib.util

def get_yaml_cases(yamlpath: str) -> list:
    '''
    获取yaml用例
    :param yamlpath: yaml 文件路径，相对于项目目录，如 "data/config.yaml"
    :return:
    '''
    yaml_data = get_yaml_data(base_utils.file_absolute_path(yamlpath))
    cases = yaml_data.get("TestDataCollections")
    config = yaml_data.get("Config")
    if not isinstance(cases,list):
        raise ValueError("用例必需是列表，请检查yaml中的用例格式")
    # 对用例数据进行渲染
    context = {}
    if isinstance(Global_Map.get(),dict):
        context.update(Global_Map.get())
    if isinstance(config,dict):
        context.update(config)
    context.update(__builtins__) # 系统内置函数
    context.update(base_utils.__dict__)  # luban-common内置函数
    if importlib.util.find_spec("expand_function"):
        expand_function = importlib.import_module("expand_function")
        context.update(expand_function.__dict__)  # 自定义拓展函数
    rend_template_any(cases, context)
    # 如果有tag时，只返回指定tag的数据
    tags = Global_Map.get("lb_case_tag")
    if tags and isinstance(tags,list):
        tags_cases = []
        for case in cases:
            if case.get("Tag") in tags:
                tags_cases.append(case)
        return tags_cases
    else:
        return cases

if __name__ == '__main__':
    #读取信息
    yamldata = get_yaml_cases(yamlpath='../data/caseConfig.yaml')
    print(yamldata)