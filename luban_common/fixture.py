#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022-11-30 23:30
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : fixture.py
# @Project : luban-common
import copy
import os
import time
import pytest
from luban_common.global_map import Global_Map
from luban_common.msg.robot import WeiXin
from luban_common.operation import yaml_file
from luban_common.base_utils import file_absolute_path
from luban_common.config import Config
from py._xmlgen import html

def pytest_addoption(parser):
    '''
    注册Pytest的命令行参数
    :param parser:
    :return:
    '''
    # 自定义的配置选项需要先注册如果，才能在ptest.ini中使用，注册方法如下
    parser.addini('message_switch', help='message_switch configuration')
    parser.addini('success_message', help='success_message configuration')
    parser.addini('is_local', help='is_local configuration')
    parser.addini('is_clear', help='is_clear configuration')
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
    group.addoption('--lb-robot',
                    default=os.getenv('lb_robot', None),
                    help='set robot')

def pytest_configure(config):
    '''
    获取配置信息
    :param config:
    :return:
    '''
    _env_config = os.getenv("lb_env", None) if os.getenv("lb_env", None) else config.getoption("--lb-env")
    _browser = os.getenv("lb_driver", None) if os.getenv("lb_driver", None) else config.getoption("--lb-driver")
    _base_url = os.getenv("lb_base_url", None) if os.getenv("lb_base_url", None) else config.getoption("--lb-base-url")
    _robot = os.getenv("lb_robot", None) if os.getenv("lb_robot", None) else config.getoption("--lb-robot")
    _is_local =  True if config.getini("is_local") == "True" else False
    _message_switch = True if config.getini("message_switch") == "True" else False
    _success_message = True if config.getini("success_message") == "True" else False
    _is_clear = True if config.getini("is_clear") == "True" else False
    pytestini = {
        "lb_env": _env_config,
        "lb_driver": _browser,
        "lb_base_url": _base_url,
        "lb_robot": _robot,
        "is_local": _is_local,
        "message_switch": _message_switch,
        "success_message": _success_message,
        "is_clear": _is_clear
    }
    if _env_config:
        if hasattr(config, "_metadata"):
            if _env_config is not None:
                config._metadata["运行配置"] = _env_config
            if _browser is not None:
                config._metadata["浏览器"] = _browser
            if _base_url is not None:
                config._metadata["基础URL"] = _base_url
            if _is_local is not None:
                config._metadata["本地载入初始化"] = _is_local
            if _message_switch is not None:
                config._metadata["消息开关"] = _message_switch
            if _success_message is not None:
                config._metadata["成功是否发送消息"] = _success_message
            if _robot is not None:
                config._metadata["机器人"] = _robot
            if _is_clear is not None:
                config._metadata["是否清理数据"] = _is_clear
        if _is_local:
            _tmp_data = yaml_file.get_yaml_data_all(os.path.join(Config.project_root_dir, "config/global"))
            if _tmp_data.get("lb_env") in _env_config or not _tmp_data.get("lb_env"):
                _global_conf = yaml_file.get_yaml_data_all(os.path.join(Config.project_root_dir, "config/global"))
            else:
                _global_conf = yaml_file.get_yaml_data_all(os.path.join(Config.project_root_dir, "config/global"), filter=["_global_map.yaml"])
        else:
            _global_conf = yaml_file.get_yaml_data_all(os.path.join(Config.project_root_dir, "config/global"), filter=["_global_map.yaml"])
        _global = {**_global_conf,**yaml_file.get_yaml_data(file_absolute_path(_env_config))}
        if _base_url:
            _global["base_url"] = _base_url
        if _robot:
            _global["weixin_robot"] = _robot
        Global_Map.sets(_global)
        Global_Map.sets(pytestini)
    else:
        raise RuntimeError("Configuration --lb-env not found")

def pytest_report_header(config):
    '''
    向terminal打印custom环境信息
    :param pytestconfig:
    :param startdir:
    :return:
    '''
    if Global_Map.get("lb_env") is not None:
        return f'lb_base_url: {Global_Map.get("lb_base_url")}, lb_driver: {Global_Map.get("lb_driver")}, lb_env: {Global_Map.get("lb_env")}'

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    '''
    收集测试结果并发送到对应IM
    '''
    # 读取消息通知配置
    weixin_robot = Global_Map.get("weixin_robot")
    message_switch = Global_Map.get("message_switch")
    success_message = Global_Map.get("success_message")
    # 定义测试结果
    total = terminalreporter._numcollected
    passed = len([i for i in terminalreporter.stats.get("passed", []) if i.when != "teardown"])
    failed = len([i for i in terminalreporter.stats.get("failed", []) if i.when != "teardown"])
    error = len([i for i in terminalreporter.stats.get("error", []) if i.when != "teardown"])
    skipped = len([i for i in terminalreporter.stats.get("skipped", []) if i.when != "teardown"])
    total_times = time.time() - terminalreporter._sessionstarttime
    html_report = config.getoption("--html")
    # 判断是否要发送消息
    if message_switch or Global_Map.get("lb_robot"):
        if weixin_robot:
            send = WeiXin()
            # 通过jenkins构件时，可以获取到JOB_NAME
            JOB_NAME = "通用" if config._metadata.get("JOB_NAME") is None else config._metadata.get("JOB_NAME")
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

def pytest_unconfigure(config):
    '''
    在退出测试过程之前调用
    :param config:
    :return:
    '''
    # 把全局变量写入到 _global_map.yaml 文件
    yaml_file.writer_yaml(file=os.path.join(Config.project_root_dir,"config/global/_global_map.yaml"), data=Global_Map.get())

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

def pytest_collection_modifyitems(items):
    # item表示每个测试用例，解决用例名称中文显示问题
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode-escape")
        item._nodeid = item._nodeid.encode("utf-8").decode("unicode-escape")

def pytest_html_results_table_header(cells):
    cells.insert(2, html.th("Description"))
    cells.pop()

def pytest_html_results_table_row(report, cells):
    cells.insert(2, html.td(report.description))
    cells.pop()
#
# @pytest.fixture(scope="session")
# def browser(pytestconfig):
#     '''
#     根据 --lb-driver 确定使用什么浏览器执行自动化
#     :param cmdopt: 调用命令行选项函数
#     :return:
#     '''
#     global driver
#     browser = pytestconfig.getoption("--lb-driver")
#     if browser is not None:
#         if browser == "chrome":
#             options = webdriver.ChromeOptions()
#             # options.add_argument('--disable-infobars')  # 禁止策略化
#             # options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
#             # options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
#             # options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
#             # options.add_argument('--incognito')  # 隐身模式（无痕模式）
#             # options.add_argument('--disable-javascript')  # 禁用javascript
#             # options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
#             options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
#             # options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
#             # options.add_argument('--user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome\User Data')  # 设置成用户自己的数据目录
#             # options.add_argument('--user-agent=iphone')   # 修改浏览器的User-Agent来伪装你的浏览器访问手机m站
#             options.add_experimental_option("excludeSwitches", ['enable-automation'])  # 禁用浏览器正在被自动化程序控制的提示（--disable-infobars 在新版本已经被弃用）
#             # options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"  # 手动指定使用的浏览器位置
#             options.add_argument('--start-maximized') # 最大化运行（全屏窗口）,不设置，取元素会报错
#             driver = webdriver.Chrome(chrome_options = options,executable_path="../../DriverPath/chromedriver.exe")
#         elif browser == "firefox":
#             driver = webdriver.Firefox(executable_path="../../DriverPath/geckodriver.exe")
#             driver.maximize_window()
#         elif browser == "ie":
#             driver = webdriver.Ie()
#         yield driver
#         driver.quit()
#     else:
#         raise RuntimeError("Configuration --lb-driver not found")
#
# @pytest.mark.hookwrapper
# def pytest_runtest_makereport(item):
#     """
#     当测试失败的时候，自动截图，展示到html报告中
#     :param item:
#     """
#     pytest_html = item.config.pluginmanager.getplugin('html')
#     outcome = yield
#     report = outcome.get_result()
#     # 对test一列重新编码，显示中文
#     report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")
#     # 当测试失败的时候，自动截图，展示到html报告中
#     extra = getattr(report, 'extra', [])
#     if report.when == 'call' or report.when == "setup":
#         xfail = hasattr(report, 'wasxfail')
#         if (report.skipped and xfail) or (report.failed and not xfail):
#             file_name = report.nodeid.replace("::", "_")+".png"
#             screen_img = _capture_screenshot()
#             if file_name:
#                 html = f'<div><img src="data:image/png;base64,{screen_img}" alt="screenshot" style="width:600px;height:300px;" ' \
#                        'onclick="window.open(this.src)" align="right"/></div>'
#                 extra.append(pytest_html.extras.html(html))
#         report.extra = extra
#         report.description = str(item.function.__doc__)
#
# @pytest.mark.optionalhook
# def pytest_html_results_table_header(cells):
#     cells.insert(1, html.th('Description'))
#     # cells.insert(1, html.th('Time', class_='sortable time', col='time'))
#     cells.pop()
#
# @pytest.mark.optionalhook
# def pytest_html_results_table_row(report, cells):
#     cells.insert(1, html.td(report.description))
#     # cells.insert(1, html.td(datetime.utcnow(), class_='col-time'))
#     cells.pop()
#
# def _capture_screenshot():
#     '''
#     截图保存为base64，展示到html中
#     :return:
#     '''
#     return driver.get_screenshot_as_base64()

if __name__ == '__main__':
    pass