#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023-9-15 21:25
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : yaml_case.py

from harmo import base_utils
from harmo.global_map import Global_Map
from harmo.operation.yaml_file import get_yaml_data
from harmo.render_template import rend_template_any
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
    case_config = yaml_data.get("Config")
    if not isinstance(cases,list):
        raise ValueError("用例必需是列表，请检查yaml中的用例格式")
    # 获取指定tag的用例，用来控制按tag执行
    tags = Global_Map.get("lb_case_tag")
    if tags and isinstance(tags,list):
        tags_cases = []
        for case in cases:
            if case.get("Tag") in tags:
                tags_cases.append(case)
        # 对用例数据进行渲染
        rend_template_any(tags_cases, get_variable(case_config))
        return tags_cases
    else:
        # 对用例数据进行渲染
        rend_template_any(cases, get_variable(case_config))
        return cases

def get_variable(config: dict) -> dict:
    '''
    获取全局变量、用例配置中的变量、内置函数、自定义拓展函数并以字典形式返回
    :param config:
    :return:
    '''
    variable_dict = {}
    # 获取全局变量
    if isinstance(Global_Map.get(),dict):
        variable_dict.update(Global_Map.get())
    # 获取传过来的配置
    if isinstance(config,dict):
        variable_dict.update(config)
    variable_dict.update(__builtins__) # 系统内置函数
    variable_dict.update(base_utils.__dict__)  # luban-common内置函数
    if importlib.util.find_spec("expand_function"):
        expand_function = importlib.import_module("expand_function")
        variable_dict.update(expand_function.__dict__)  # 自定义拓展函数
    return variable_dict

if __name__ == '__main__':
    #读取信息
    yamldata = get_yaml_cases(yamlpath='../data/caseConfig.yaml')
    print(yamldata)