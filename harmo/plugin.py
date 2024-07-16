#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022-12-3 18:14
# @Author : hubiao
# @Email : 250021520@qq.com
# @File : plugin.py

import inspect
import os
import time
from pathlib2 import Path

import pytest
import types
from _pytest.python import Module
from pytest_metadata.plugin import metadata_key
from harmo.global_map import Global_Map
from harmo.msg.robot import WeiXin
from harmo.operation import yaml_file
from harmo.base_utils import file_absolute_path
from harmo.config import Config
from py._xmlgen import html

def pytest_addhooks(pluginmanager):
    from harmo import hooks
    pluginmanager.add_hookspecs(hooks)

def pytest_addoption(parser):
    '''
    注册Pytest的命令行参数
    :param parser:
    :return:
    '''
    # 注册命令行参数
    group = parser.getgroup('harmo', "Harmo")
    group.addoption('--h-driver',
                    action="store",
                    default=os.getenv('h_driver', 'chrome'),
                    choices=['chrome', 'firefox', 'ie'],
                    help='Browser engine which should be used.')
    group.addoption('--h-base-url',
                    action="store",
                    default=os.getenv('h_base_url', None),
                    help='base url for the application under test.')
    group.addoption('--h-env',
                    action="store",
                    default=os.getenv('h_env', None),
                    help='set testing environment.')
    group.addoption('--h-robot',
                    action="store",
                    default=os.getenv('h_robot', None),
                    help='set robot.')
    group.addoption('--h-msg-name',
                    action="store",
                    default=os.getenv('h_msg_name', None),
                    help='set robot msg name.')
    group.addoption('--h-case-tag',
                    action="append",
                    default=os.getenv('h_case_tags', None),
                    help='Set the use case tags to be executed.')
    # 自定义的配置选项，需要先注册才能在ptest.ini中使用，注册方法如下
    parser.addini('message_switch', type="bool", default=False, help='message_switch configuration.')
    parser.addini('success_message', type="bool", default=False, help='success_message configuration.')
    parser.addini('case_message', type="bool", default=False, help='case_message configuration.')
    parser.addini('is_local', type="bool", default=False, help='is_local configuration.')
    parser.addini('is_clear', type="bool", default=True, help='is_clear configuration.')
    parser.addini('schema_check', type="bool", default=False, help='schema_check configuration.')
    parser.addini('custom_config', type='linelist' ,help='custom_config configuration.')

def pytest_configure(config):
    '''
    获取配置信息
    :param config:
    :return:
    '''
    _env_config = os.getenv("h_env", None) if os.getenv("h_env", None) else config.getoption("--h-env")
    _browser = os.getenv("h_driver", None) if os.getenv("h_driver", None) else config.getoption("--h-driver")
    _base_url = os.getenv("h_base_url", None) if os.getenv("h_base_url", None) else config.getoption("--h-base-url")
    _robot = os.getenv("h_robot", None) if os.getenv("h_robot", None) else config.getoption("--h-robot")
    _msg_name = os.getenv("h_msg_name", None) if os.getenv("h_msg_name", None) else config.getoption("--h-msg-name")
    _case_tag = os.getenv("h_case_tag", None) if os.getenv("h_case_tag", None) else config.getoption("--h-case-tag")
    _message_switch = config.getini("message_switch")
    _success_message = config.getini("success_message")
    _case_message = config.getini("case_message")
    _is_local =  config.getini("is_local")
    _is_clear = config.getini("is_clear")
    _schema_check = config.getini("schema_check")
    _custom_config_temp = config.getini("custom_config")
    _custom_config = {}
    if _custom_config_temp:
        for cfg in _custom_config_temp:
            cfg_list = cfg.split(":",1)
            if len(cfg_list) >1:
                if cfg_list[1].strip().lower() == "false":
                    value = False
                elif cfg_list[1].strip().lower() == "true":
                    value = True
                else:
                    value = cfg_list[1].strip()
                _custom_config.update({cfg_list[0].strip():value})
    if _env_config:
        if _is_local:
            _tmp_data = yaml_file.get_yaml_data_all(os.path.join(Config.project_root_dir, "config/global"))
            if not _tmp_data.get("h_env") or _tmp_data.get("h_env") in _env_config:
                _global_conf = _tmp_data
            else:
                _global_conf = yaml_file.get_yaml_data_all(os.path.join(Config.project_root_dir, "config/global"), filter=["_global_map.yaml","_global_map_temp.yaml"])
        else:
            _global_conf = yaml_file.get_yaml_data_all(os.path.join(Config.project_root_dir, "config/global"), filter=["_global_map.yaml","_global_map_temp.yaml"])
        _global = {**_global_conf,**yaml_file.get_yaml_data(file_absolute_path(_env_config))}
        if _base_url:
            _global["base_url"] = _base_url
        if _robot:
            _global["weixin_robot"] = _robot
        pytestini = {
            "h_env": _env_config,
            "h_driver": _browser,
            "h_base_url": _base_url,
            "h_robot": _robot,
            "h_msg_name": _msg_name,
            "h_case_tag": _case_tag,
            "message_switch": _message_switch,
            "success_message": _success_message,
            "case_message": _case_message,
            "is_local": _is_local,
            "is_clear": _is_clear,
            "schema_check": _schema_check,
            "custom_config": _custom_config
        }
        Global_Map.sets(_global)
        Global_Map.sets(pytestini)
        # 写metadata
        metadata = config.pluginmanager.getplugin("metadata")
        if metadata:
            if _env_config is not None:
                config.stash[metadata_key]["运行配置"] = _env_config
            if _browser is not None:
                config.stash[metadata_key]["浏览器"] = _browser
            if _global.get("base_url"):
                config.stash[metadata_key]["基础URL"] = _global.get("base_url")
            if _is_local is not None:
                config.stash[metadata_key]["本地载入初始化"] = _is_local
            if _message_switch is not None:
                config.stash[metadata_key]["消息开关"] = _message_switch
            if _success_message is not None:
                config.stash[metadata_key]["成功消息提醒"] = _success_message
            if _case_message is not None:
                config.stash[metadata_key]["用例失败提醒"] = _case_message
            if _global.get("weixin_robot"):
                config.stash[metadata_key]["机器人ID"] = _global.get("weixin_robot")
            if _is_clear is not None:
                config.stash[metadata_key]["是否清理数据"] = _is_clear
            if _case_tag is not None:
                config.stash[metadata_key]["执行用例tag"] = _case_tag
            if _schema_check is not None:
                config.stash[metadata_key]["schema检查状态"] = _schema_check
            if _custom_config is not None:
                config.stash[metadata_key]["其它自定义配置"] = _custom_config

def pytest_report_header(config):
    '''
    向terminal打印custom环境信息
    :param config:
    :return:
    '''
    if Global_Map.get("h_env") is not None:
        return f'h_base_url: {Global_Map.get("h_base_url")}, h_driver: {Global_Map.get("h_driver")}, h_env: {Global_Map.get("h_env")}'

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    '''
    收集测试结果并发送到对应IM
    '''
    # 读取消息通知配置
    weixin_robot = Global_Map.get("weixin_robot")
    message_switch = Global_Map.get("message_switch")
    success_message = Global_Map.get("success_message")
    h_msg_name = Global_Map.get("h_msg_name")
    # 定义测试结果
    total = terminalreporter._numcollected
    passed = len([i for i in terminalreporter.stats.get("passed", []) if i.when != "teardown"])
    failed = len([i for i in terminalreporter.stats.get("failed", []) if i.when != "teardown"])
    error = len([i for i in terminalreporter.stats.get("error", []) if i.when != "teardown"])
    skipped = len([i for i in terminalreporter.stats.get("skipped", []) if i.when != "teardown"])
    total_times = time.time() - terminalreporter._sessionstarttime
    html_report = config.getoption("--html")
    # 判断是否要发送消息
    if message_switch or weixin_robot:
        if weixin_robot:
            # 通过jenkins构件时，可以获取到JOB_NAME
            if h_msg_name:
                JOB_NAME = h_msg_name
            else:
                JOB_NAME = "通用" if config.stash[metadata_key].get("JOB_NAME") is None else config.stash[metadata_key].get("JOB_NAME")
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
                WeiXin().send_message_markdown(hookkey=weixin_robot,content=markdown_content)
                if html_report:
                    WeiXin().send_file(hookkey=weixin_robot, file=html_report)
            elif success_message:
                markdown_content = f'''
                                    # 恭喜 <font color=\'info\'>{JOB_NAME}</font> 巡检通过，请放心
                                    >通知范围：@全部成员
                                    >本次共执行 **{total}** 条用例，<font color=\'info\'>**全部执行通过**</font>，耗时 **{round(total_times,2)}** 秒
                                    >
                                    >可点击下方 report 文件查看详情'''
                WeiXin().send_message_markdown(hookkey=weixin_robot, content=markdown_content)
                if html_report:
                    WeiXin().send_file(hookkey=weixin_robot, file=html_report)
        else:
            print("配置文件中 weixin_robot 未配置，无法发送报告")

def pytest_unconfigure(config):
    '''
    在退出测试过程之前调用
    :param config:
    :return:
    '''

    # 有h_env表示使用到了harmo，然后把全局变量写入到 _global_map_temp.yaml 文件
    if Global_Map.get("h_env"):
        yaml_file.writer_yaml(file=os.path.join(Config.project_root_dir,"config/global/_global_map_temp.yaml"), data=Global_Map.get())
    # unregister plugin

def pytest_collection_modifyitems(items):
    marker_all = []
    for item in items:
        # 获取每个用例的 marker 名称，并汇聚成 marker_all
        for marker in item.iter_markers():
            marker_all.append(marker.name)
        Global_Map.set("marker_all",list(set(marker_all)))
        # item表示每个测试用例，解决用例名称中文显示问题
        item.name = item.name.encode("utf-8").decode("unicode-escape")
        item._nodeid = item._nodeid.encode("utf-8").decode("unicode-escape")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    每个测试用例运行结束后，如果失败发送消息通知
    :param item:
    """
    out = yield
    report = out.get_result()
    # 用例失败时
    if report.when == "call" and report.outcome == "failed":
        weixin_robot = Global_Map.get("weixin_robot")
        message_switch = Global_Map.get("message_switch")
        # 判断是否要发送消息
        if message_switch or weixin_robot:
            if weixin_robot and Global_Map.get("case_message"):
                ds = str.strip(item.function.__doc__) if item.function.__doc__ else item.function.__name__
                md = f'''
                        # 用例 {ds} `{report.outcome}`
                        >用例名称：<font color="comment">{item.function.__name__}</font>
                        >用例描述：<font color="comment">{str.strip(item.function.__doc__) if item.function.__doc__ else "无"}</font>
                        >用例位置：<font color="comment">{report.nodeid}</font>
                        >失败原因：<font color="comment">{call.excinfo}</font>'''
                if Global_Map.get("temp_user_properties"):
                    if Global_Map.get("temp_user_properties").get("url"):
                        md += f'''\n>接口URL：<font color="comment">{Global_Map.get("temp_user_properties").get("url")}</font>'''
                    if Global_Map.get("temp_user_properties").get("status_code"):
                        md += f'''\n>响应码：<font color="comment">{Global_Map.get("temp_user_properties").get("status_code")}</font>'''
                if len(md.encode()) > 4096:
                    print("最长不能超过4096个字节")
                else:
                    WeiXin().send_message_markdown(hookkey=weixin_robot, content=md)
    # 删除临时变量
    Global_Map.del_key("temp_user_properties")

# def pytest_html_results_table_header(cells):
#     cells.insert(2, html.th("Description"))
#     cells.pop()
#
# def pytest_html_results_table_row(report, cells):
#     cells.insert(2, html.td(report.description))
#     cells.pop()
#
# @pytest.fixture(scope="session")
# def browser(pytestconfig):
#     '''
#     根据 --h-driver 确定使用什么浏览器执行自动化
#     :param cmdopt: 调用命令行选项函数
#     :return:
#     '''
#     global driver
#     browser = pytestconfig.getoption("--h-driver")
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
#         raise RuntimeError("Configuration --h-driver not found")
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
def get_fixture():
    """
    获取fixtures目录下以fixture开头的py文件
    :return: fixture路径列表
    """
    _fixtures_dir = os.path.join(Config.project_root_dir,"fixtures")
    _fixtures = []
    # 项目目录fixtures目录下的fixture
    for root, _, files in os.walk(_fixtures_dir):
        for file in files:
            if file.startswith("fixture") and file.endswith(".py"):
                full_path = os.path.join(root, file)
                import_path = full_path.replace(_fixtures_dir, "").replace("\\", ".").replace("/", ".").replace(".py", "")
                _fixtures.append("fixtures" + import_path)
    return _fixtures

def all_plugins():
    '''
    获取全部插件
    :return:
    '''
    # 设置项目目录
    _caller = inspect.stack()[1]
    Config.project_root_dir = os.path.dirname(_caller.filename)
    # 获取全部插件
    _fixtures = get_fixture()
    return _fixtures

if __name__ == '__main__':
    pass