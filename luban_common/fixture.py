#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022-11-30 23:30
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : fixture.py
# @Project : luban-common

import os
import time

import pytest

from luban_common.global_map import Global_Map
from luban_common.msg.robot import WeiXin
from luban_common.operation import yaml_file
from luban_common.base_utils import file_absolute_path
from luban_common.config import Config


def pytest_addoption(parser):
    '''
    注册Pytest的命令行参数
    :param parser:
    :return:
    '''
    # 自定义的配置选项需要先注册如果，才能在ptest.ini中使用，注册方法如下
    # parser.addini('email_subject', help='test reports email subject')
    parser.addini('globalConf', help='global configuration')
    parser.addini('message_switch', help='message_switch configuration')
    parser.addini('success_message', help='success_message configuration')
    parser.addini('load_locally', help='load_locally configuration')
    # 注册命令行参数
    group = parser.getgroup('testing environment configuration')
    group.addoption('--lb-driver',
                    default=os.getenv('lb_driver', 'chrome'),
                    choices=['chrome', 'firefox', 'ie'],
                    help='set Browser')
    group.addoption('--lb-base-url',
                    default=os.getenv('lb_base_url', None),
                    help='base url for the application under test')
    group.addoption('--lb-env',
                    default=os.getenv('lb_env', None),
                    help='set testing environment')

def pytest_configure(config):
    '''
    在测试报告中添加环境信息
    :param config:
    :return:
    '''
    envConf = os.getenv("lb_env", None) if os.getenv("lb_env", None) else config.getoption("--lb-env")
    browser = os.getenv("lb_driver", None) if os.getenv("lb_driver", None) else config.getoption("--lb-driver")
    baseUrl = os.getenv("lb_base_url", None) if os.getenv("lb_base_url", None) else config.getoption("--lb-base-url")
    _load_locally = config.getini("load_locally")
    if hasattr(config, "_metadata"):
        if envConf is not None:
            config._metadata["运行配置"] = envConf
        if browser is not None:
            config._metadata["浏览器"] = browser
        if baseUrl is not None:
            config._metadata["基础URL"] = baseUrl
        if _load_locally is not None:
            config._metadata["本地载入初始化"] = _load_locally

def pytest_report_header(config):
    '''
    向terminal打印custom环境信息
    :param pytestconfig:
    :param startdir:
    :return:
    '''
    envConf = os.getenv("lb_env", None) if os.getenv("lb_env", None) else config.getoption("--lb-env")
    browser = os.getenv("lb_driver", None) if os.getenv("lb_driver", None) else config.getoption("--lb-driver")
    baseUrl = os.getenv("lb_base_url", None) if os.getenv("lb_base_url", None) else config.getoption("--lb-base-url")
    if envConf is not None:
        return f'lb_driver: {browser}, lb_base_url: {baseUrl}, lb_env: {envConf}'

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    '''收集测试结果并发送到对应IM'''
    # 读取配置文件中的robot
    envConf = os.getenv("lb_env", None) if os.getenv("lb_env", None) else config.getoption('--lb-env')
    envConfDate = yaml_file.get_yaml_data(file_absolute_path(envConf))
    weixin_robot = envConfDate.get('weixin_robot')
    # 定义测试结果
    total = terminalreporter._numcollected
    passed = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    failed = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    error = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    skipped = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    total_times = time.time() - terminalreporter._sessionstarttime
    message_switch = True if config.getini('message_switch') == 'True' else False
    success_message = True if config.getini('success_message') == 'True' else False
    html_report = config.getoption('--html')
    # 判断是否要发送消息
    if message_switch:
        if weixin_robot:
            send = WeiXin()
            # 通过jenkins构件时，可以获取到JOB_NAME
            JOB_NAME = '通用' if config._metadata.get('JOB_NAME') is None else config._metadata.get('JOB_NAME')
            if failed + error != 0:
                markdown_content = f'''
                                    # 警告！`{JOB_NAME}` 巡检出现异常
                                    >通知范围：@所有人
                                    >本次共执行 **{total}** 条用例
                                    >有 <font color=\'info\'>**{passed}**</font> 条执行成功
                                    >有 <font color='warning'>**{failed}**</font> 条执行失败
                                    >有 `**{error}**` 条执行出错
                                    >有 <font color=\'comment\'>**{skipped}**</font> 条跳过
                                    >共耗时 <font color=\'comment\'>**{round(total_times,2)}**</font> 秒
                                    >
                                    >可点击下方 report 文件查看详情'''
                send.send_message_markdown(hookkey=weixin_robot,content=markdown_content)
                if html_report:
                    send.send_file(hookkey=weixin_robot, file=html_report)
            elif success_message:
                markdown_content = f'''
                                    # 恭喜 <font color=\'info\'>{JOB_NAME}</font> 巡检通过，请放心
                                    >通知范围：@全部成员
                                    >本次共执行 **{total}** 条用例，<font color=\'info\'>**全部执行通过**</font>，耗时 **{round(total_times,2)}** 秒
                                    >
                                    >可点击下方 report 文件查看详情'''
                send.send_message_markdown(hookkey=weixin_robot, content=markdown_content)
                if html_report:
                    send.send_file(hookkey=weixin_robot, file=html_report)
        else:
            print("配置文件中 weixin_robot 未配置，无法发送报告")

@pytest.fixture(scope='session')
def env_conf(pytestconfig):
    '''
    获取lb-env和global环境配置文件
    :return:
    '''
    _env_config = os.getenv("lb_env", None) if os.getenv("lb_env", None) else pytestconfig.getoption('--lb-env')
    _global_conf_date = yaml_file.get_yaml_data_all(os.path.join(Config.project_root_dir,"config/global"))
    _globalConf = pytestconfig.getini('globalConf')
    _baseUrl = os.getenv("lb_base_url", None) if os.getenv("lb_base_url", None) else pytestconfig.getoption('--lb-base-url')
    if _env_config:
        _global_conf_date = {**_global_conf_date,**yaml_file.get_yaml_data(file_absolute_path(_env_config))}
        if _baseUrl:
            _global_conf_date["base_url"] = _baseUrl
        if _globalConf:
            return {**_global_conf_date, **yaml_file.get_yaml_data(file_absolute_path(_globalConf))}
        Global_Map.sets(_global_conf_date)
        return _global_conf_date
    else:
        raise RuntimeError('Configuration --lb-env not found')

@pytest.fixture(scope='session')
def base_url(pytestconfig):
    '''
    base URL
    :return:
    '''
    base_url = os.getenv("lb_base_url", None) if os.getenv("lb_base_url", None) else pytestconfig.getoption('--lb-base-url')
    if base_url:
        return base_url
    else:
        raise RuntimeError('--lb-base-url not found')

@pytest.fixture(scope='session')
def global_cache(request):
    '''
    全局缓存，当前执行生命周期有效
    :param request:
    :return:
    '''
    return request.config.cache

if __name__ == '__main__':
    pass