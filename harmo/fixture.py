#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022-11-30 23:30
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : fixture.py

import copy
import os
import pytest
from harmo.global_map import Global_Map

@pytest.fixture(scope="session")
def env_conf(pytestconfig):
    '''
    获取h-env和global环境配置文件
    :return:
    '''
    return copy.deepcopy(Global_Map.get())

@pytest.fixture(scope="session")
def base_url(pytestconfig):
    '''
    base URL
    :return:
    '''
    _base_url = os.getenv("h_base_url", None) if os.getenv("h_base_url", None) else pytestconfig.getoption("--h-base-url")
    if _base_url:
        return _base_url
    else:
        raise RuntimeError("--h-base-url not found")

if __name__ == '__main__':
    pass