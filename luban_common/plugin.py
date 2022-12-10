#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022-12-3 18:14
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : plugin.py

import inspect
import os

from luban_common.config import Config

def get_fixture():
    """
    获取luban-common和fixtures目录下的fixture
    :return: fixture路径列表
    """
    _fixtures_dir = os.path.join(Config.project_root_dir,"fixtures")
    fixtures = []
    # 项目目录fixtures目录下的fixture
    for root, _, files in os.walk(_fixtures_dir):
        for file in files:
            if file.startswith("fixture") and file.endswith(".py"):
                full_path = os.path.join(root, file)
                import_path = full_path.replace(_fixtures_dir, "").replace("\\", ".").replace("/", ".").replace(".py", "")
                fixtures.append("fixtures" + import_path)
    # luban-common框架自带的fixture
    fixtures.append("luban_common.fixture")
    return fixtures

def all_plugins():
    '''

    :return:
    '''
    # 设置项目目录
    caller = inspect.stack()[1]
    Config.project_root_dir = os.path.dirname(caller.filename)
    # 获取全部插件
    plugins = get_fixture()
    return plugins

if __name__ == '__main__':
    print(all_plugins())