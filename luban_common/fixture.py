#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022-11-30 23:30
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : fixture.py
# @Project : luban-common

import copy
import os
import pytest
from luban_common.global_map import Global_Map

@pytest.fixture(scope="session")
def env_conf(pytestconfig):
    '''
    获取lb-env和global环境配置文件
    :return:
    '''
    return copy.deepcopy(Global_Map.get())

@pytest.fixture(scope="session")
def base_url(pytestconfig):
    '''
    base URL
    :return:
    '''
    _base_url = os.getenv("lb_base_url", None) if os.getenv("lb_base_url", None) else pytestconfig.getoption("--lb-base-url")
    if _base_url:
        return _base_url
    else:
        raise RuntimeError("--lb-base-url not found")

if __name__ == '__main__':
    pass