#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/2/15 20:00
# @Author  : hubiao


from cleo import Command as BaseCommand

CONFTEST_DEFAULT = u"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TIME    : 2018/10/9 18:07
# Author  : hubiao
# File    : conftest.py
import os
import time

import pytest
from luban_common import base_requests
from luban_common.msg.weixin import WeiXinMessage
from luban_common.msg.youdu import send_youdu
from luban_common.operation import yaml_file

from business import public_login
from swagger.jump import Jump
from utils.utils import file_absolute_path


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
    # 注册命令行参数
    group = parser.getgroup("testing environment configuration")
    group.addoption("--lb-driver",
                    default=os.getenv("Pytest_Driver", "chrome"),
                    choices=["chrome", "firefox", "ie"],
                    help="set Browser")
    group.addoption("--lb-base-url",
                    default=os.getenv("Pytest_Base_Url", None),
                    help="base url for the application under test")
    group.addoption("--lb-env",
                    default=os.getenv("Pytest_Env", None),
                    help="set testing environment")


def pytest_configure(config):
    '''
    在测试报告中添加环境信息
    :param config:
    :return:
    '''
    envConf = config.getoption("--lb-env")
    browser = config.getoption("--lb-driver")
    baseUrl = config.getoption("--lb-base-url")
    if hasattr(config, '_metadata'):
        if browser is not None:
            config._metadata['Browser'] = browser
        if envConf is not None:
            config._metadata['EnvConf'] = envConf
        if baseUrl is not None:
            config._metadata['BaseUrl'] = baseUrl


def pytest_report_header(config):
    '''
    向terminal打印custom环境信息
    :param config:
    :param startdir:
    :return:
    '''
    envConf = config.getoption("--lb-env")
    browser = config.getoption("--lb-driver")
    baseUrl = config.getoption("--lb-base-url")
    if envConf:
        return f"browser: {browser}, baseUrl: {baseUrl}, configuration: {envConf}"

@pytest.fixture(scope="session")
def env_conf(pytestconfig):
    '''
    获取lb-env和globalConf环境配置文件
    :return:
    '''
    envConf = pytestconfig.getoption("--lb-env")
    globalConf = pytestconfig.getini("globalConf")
    if envConf:
        if globalConf:
            return {**yaml_file.get_yaml_data(file_absolute_path(envConf)), **yaml_file.get_yaml_data(file_absolute_path(globalConf))}
        return yaml_file.get_yaml_data(file_absolute_path(envConf))
    else:
        raise RuntimeError("Configuration --lb-env not found")


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    '''
    base URL
    :return:
    '''
    base_url = pytestconfig.getoption('--lb-base-url')
    if base_url:
        return base_url


@pytest.fixture(scope="session")
def global_cache(request):
    '''
    全局缓存，当前执行生命周期有效
    :param request:
    :return:
    '''
    return request.config.cache

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    '''收集测试结果'''
    # 读取配置文件
    envConf = yaml_file.get_yaml_data(file_absolute_path(config.getoption("--lb-env")))
    # 定义测试结果
    total = terminalreporter._numcollected
    passed = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    failed = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    error = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    skipped = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    success_rate =len(terminalreporter.stats.get('passed', []))/terminalreporter._numcollected*100
    total_times = time.time() - terminalreporter._sessionstarttime
    message_switch = True if config.getini("message_switch") == "True" else False
    success_message = True if config.getini("success_message") == "True" else False
    # 判断是否要发送消息
    if message_switch:
        send = WeiXinMessage()
        youdu_users = envConf.get("youdu_users")
        weixin_toparty = envConf.get("weixin_toparty")
        if failed + error != 0:
            content = f"共执行 {total} 条用例，有 {passed} 条执行成功，有 {failed} 条执行失败，有 {error} 条执行出错，跳过 {skipped} 条"
            if weixin_toparty:
                send.send_message_textcard(title="警告！自动化巡检测试出现异常", content=content, toparty=weixin_toparty)
            if youdu_users:
                send_youdu(title="警告！自动化巡检测试出现异常", content="测试一下", sendTo=youdu_users, session=0)
        else:
            if success_message:
                content = f"共执行 {total} 条用例，全部执行通过，共耗时 {round(total_times,2)} 秒，请放心"
                if weixin_toparty:
                    send.send_message_textcard(title="恭喜，自动化巡检测试通过", content=content, toparty=weixin_toparty)
                if youdu_users:
                    send_youdu(title="恭喜，自动化巡检测试通过", content=content, sendTo=youdu_users, session=0)

@pytest.fixture(scope="session")
def bimadmin_login(env_conf, global_cache):
    '''
    BIM Aadmin运维管理系统登录
    :return:
    '''
    BimAdminLogin = public_login.BimAdmin(env_conf).login()
    yield BimAdminLogin


@pytest.fixture(scope="session")
def center_cas(env_conf, global_cache):
    '''
    获取Center CAS登录凭证
    :return:
    '''
    public_login.Center(env_conf["center"]["username"], env_conf["center"]["password"], env_conf, global_cache).login()
    yield


@pytest.fixture(scope="session")
def center_builder(center_cas, env_conf, global_cache):
    '''
    获取Builder登录凭证
    :return:
    '''
    CenterBuilder = base_requests.Send(global_cache.get("builder", False), env_conf, global_cache)
    yield CenterBuilder


@pytest.fixture(scope="session")
def center_process(center_cas, env_conf, global_cache):
    '''
    获取Process登录凭证
    :return:
    '''
    CenterProcess = base_requests.Send(global_cache.get("process", False), env_conf, global_cache)
    yield CenterProcess


@pytest.fixture(scope="session")
def iworks_app_cas(env_conf, global_cache):
    '''
    获取PDS登录凭证
    :return:
    '''
    public_login.IworksApp(env_conf["iworksApp"]["username"], env_conf["iworksApp"]["password"], env_conf, global_cache).login()
    yield


@pytest.fixture(scope="session")
def lbbv(iworks_app_cas, env_conf, global_cache):
    '''
    获取LBBV登录凭证
    :return:
    '''
    LBBV = base_requests.Send(global_cache.get("lbbv", False), env_conf, global_cache)
    yield LBBV


@pytest.fixture(scope="session")
def bimco(iworks_app_cas, env_conf, global_cache):
    '''
    获取BimCO登录凭证
    :return:
    '''
    BimCO = base_requests.Send(global_cache.get("bimco", False), env_conf, global_cache)
    yield BimCO


@pytest.fixture(scope="session")
def process(iworks_app_cas, env_conf, global_cache):
    '''
    获取Process登录凭证
    :return:
    '''
    Process = base_requests.Send(global_cache.get("lbprocess", False), env_conf, global_cache)
    yield Process


@pytest.fixture(scope="session")
def pds_common(iworks_app_cas, env_conf, global_cache):
    '''
    获取PDSCommon登录凭证
    :return:
    '''
    PDSCommon = base_requests.Send(global_cache.get("pdscommon", False), env_conf, global_cache)
    yield PDSCommon

@pytest.fixture(scope="session")
def pds_doc(iworks_app_cas, env_conf, global_cache):
    '''
    获取pdsdoc登录凭证
    :return:
    '''
    PDSDoc = base_requests.Send(global_cache.get("pdsdoc", False), env_conf, global_cache)
    yield PDSDoc

@pytest.fixture(scope="session")
def builder_common_business_data(iworks_app_cas, env_conf, global_cache):
    '''
    获取BusinessData登录凭证
    :return:
    '''
    builderCommonBusinessData = base_requests.Send(global_cache.get("buildercommonbusinessdata", False), env_conf, global_cache)
    yield builderCommonBusinessData

@pytest.fixture(scope="session")
def bimapp_login(env_conf, global_cache):
    '''
    BIMApp 通行证系统登录
    :return:
    '''
    BimAppLogin = public_login.Bimapp(env_conf["bimapp"]["username"], env_conf["bimapp"]["password"], env_conf,
                                      global_cache).login()
    yield BimAppLogin


@pytest.fixture(scope="session")
def myluban_web_login(env_conf, global_cache):
    '''
    Myluban web 登录
    :return:
    '''
    MylubanWebLogin = public_login.MylubanWeb(env_conf["MylubanWeb"]["username"], env_conf["MylubanWeb"]["password"],
                                              env_conf, global_cache).login()
    yield MylubanWebLogin


@pytest.fixture(scope="session")
def bussiness_login(env_conf, global_cache):
    '''
    Bussiness 业务管理系统登录
    :return:
    '''
    BussinessLogin = public_login.Bussiness(env_conf["Bussiness"]["username"], env_conf["Bussiness"]["password"], env_conf,
                                            global_cache).login()
    yield BussinessLogin


@pytest.fixture(scope="session")
def lubansoft_login(env_conf, global_cache):
    '''
    算量软件登录
    :return:
    '''
    LubansoftLogin = public_login.LubanSoft(env_conf["lubansoft"]["username"], env_conf["lubansoft"]["password"], env_conf,
                                            global_cache).login()
    yield LubansoftLogin


@pytest.fixture(scope="session")
def iworks_web_cas(env_conf, global_cache):
    '''
    获取cas登录凭证
    :return:
    '''
    public_login.IworksWeb(env_conf["iworksWeb"]["username"], env_conf["iworksWeb"]["password"], env_conf, global_cache).login()
    yield

@pytest.fixture(scope="session")
def iworks_web_common(iworks_web_cas, env_conf, global_cache):
    '''
    获取common登录凭证
    :return:
    '''
    resule = base_requests.Send(global_cache.get("pdscommon", False), env_conf, global_cache)
    # 处理第一次 302跳转接口不能是post、put、update接口,必须用get接口调用
    Jump().jump(resule,resource='/rs/jump')
    yield resule

@pytest.fixture(scope="session")
def iworks_web_process(iworks_web_cas, env_conf, global_cache):
    '''
    获取process登录凭证
    :return:
    '''
    resule = base_requests.Send(global_cache.get("LBprocess", False), env_conf, global_cache)
    # 处理第一次 302跳转接口不能是post、put、update接口,必须用get接口调用
    Jump().jump(resule,resource='/process/jump')
    yield resule

@pytest.fixture(scope="session")
def iworks_web_businessdata(iworks_web_cas, env_conf, global_cache):
    '''
    获取businessdata登录凭证
    :return:
    '''
    resule = base_requests.Send(global_cache.get("BuilderCommonBusinessdata", False), env_conf, global_cache)
    # 处理第一次 302跳转接口不能是post、put、update接口,必须用get接口调用
    Jump().jump(resule,resource='/jump')
    yield resule

@pytest.fixture(scope="session")
def iworks_web_plan(iworks_web_cas, env_conf, global_cache):
    '''
    获取plan登录凭证
    :return:
    '''
    resule = base_requests.Send(global_cache.get("LBSP", False), env_conf, global_cache)
    # 处理第一次 302跳转接口不能是post、put、update接口,必须用get接口调用
    Jump().jump(resule,resource='/rs/jump')
    yield resule

@pytest.fixture(scope="session")
def iworks_web_doc(iworks_web_cas, env_conf, global_cache):
    '''
    获取doc登录凭证
    :return:
    '''
    resule = base_requests.Send(global_cache.get("pdsdoc", False), env_conf, global_cache)
    # 处理第一次 302跳转接口不能是post、put、update接口,必须用get接口调用
    Jump().jump(resule,resource='/jump')
    yield resule

@pytest.fixture(scope="session")
def iworks_web_bimco(iworks_web_cas, env_conf, global_cache):
    '''
    获取bimco登录凭证
    :return:
    '''
    resule = base_requests.Send(global_cache.get("bimco", False), env_conf, global_cache)
    # 处理第一次 302跳转接口不能是post、put、update接口,必须用get接口调用
    Jump().jump(resule,resource='/rs/co/jump')
    yield resule

@pytest.fixture(scope="session")
def iworks_web_pdsdoc(iworks_web_cas, env_conf, global_cache):
    '''
    获取bimco登录凭证
    :return:
    '''
    resule = base_requests.Send(global_cache.get("pdsdoc", False), env_conf, global_cache)
    # 处理第一次 302跳转接口不能是post、put、update接口,必须用get接口调用
    Jump().jump(resule,resource='/rs/jump')
    yield resule"""

GLOBAL_CONFIG_DEFAULT = """weixin :
  corpid : ww7cfc110509f4c78c
  secret : 0fmsVQuSrClZG9225BjvpiSdPCBuaQdukPY
  agentid : 100000
centerProductid : 100
iworksAppProductId : 94
iworksWebProductId: 192
headers:
    multipart_header : '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400","Accept-Encoding": "gzip, deflate","Accept-Language": "zh-CN,zh;q=0.8"}'
    json_header : '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400","Content-Type": "application/json","Accept-Encoding": "gzip, deflate","Accept-Language": "zh-CN,zh;q=0.8"}'
    urlencoded_header : '{"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400","Content-Type": "application/x-www-form-urlencoded","Accept-Encoding": "gzip, deflate","Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"}'
    plain_header : '{"Accept": "text/plain","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400","Content-Type": "application/x-www-form-urlencoded;charset=utf-8","Accept-Encoding": "gzip, deflate","Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"}'
    soap_header : '{"Content-Type": "text/xml;charset=utf-8","Accept-Encoding": "gzip, deflate","SOAPAction": ""}'"""

CONFIG_DEFAULT = """pds : http://app.lbuilder.cn
youdu_users: "胡彪_吴国君"
weixin_toparty: 2
center:
  username: lb91247
  password: 264f0c676e143da03019f1698304c468
iworksApp :
  username : test
  password : 96e79218965eb72c92a549dd5a325612
  clientVersion: 1.9.0"""

PYTESTINI_DEFAULT = """[pytest]
addopts =
    --lb-env=Config/release/config.yaml
    --lb-driver=firefox
    --html=reports/report.html
    -p no:warnings
;    --cache-clear
globalConf = Config/globalConf.yaml
minversion = 5.0
testpaths = testcases testsuites
message_switch = True
success_message = False
log_cli = True
log_cli_level = ERROR
log_cli_format = %(asctime)s %(levelname)s %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S"""

UTILS_DEFAULT = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2020/7/5 9:47
# @Author  : hubiao
# @File    : utils.py
import os

def file_absolute_path(rel_path):
    '''
    通过文件相对路径，返回文件绝对路径
    :param rel_path: 相对于项目根目录的路径，如data/check_lib.xlsx
    :return:
    '''
    current_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(current_path,'..', rel_path)
    return file_path

@allure.step("上传文件")
def upFiles(pdscommon, resource, filePath):
    '''
    封装上传文件方法，要求传二个参数，上传成功返回文件UUID
    pdscommon：所属项目
    resource：请求的地址
    filePath：要上传的文件，相对于项目根目录，如 data/Doc/Lubango20191205.docx
    :return: 返回文件uuid
    '''
    file = base_utils.file_is_exist(filePath)
    try:
        response = pdscommon.request('post', resource, files={'file': open(file, 'rb')})
        return response["Response_body"]
    except Exception as e:
        raise FileNotFoundError(f"上传文件失败，错误原因:{e}")"""

GIT_DEFAULT = """__pycache__
.DS_Store
.cache
.eggs
.pytest_cache
.vscode
.idea
.pypirc
.venv
.tox
*/tmp/*
*.egg-info
*.pyc
dist
build
logs
reports"""

PUBLIC_LOGIN = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2019/1/2 11:19
# @Author  : hubiao
# @File    : public_login.py
import json
import re
import xmltodict

from luban_common import base_utils
from luban_common import base_requests
from luban_common.base_assert import Assertions


class BimAdmin:
    '''
    BimAdmin 登录类
    '''
    def __init__(self,envConf):
        self.header = envConf["headers"]["urlencoded_header"]
        self.body = envConf["sysadmin"]["logininfo"]
        self.BimAdminLogin = base_requests.Send(envConf["sysadmin"]["host"], envConf)

    def login(self):
        '''
        后台登录
        :param BimAadminLogin:
        :return:
        '''
        resource = "/login.htm"
        response = self.BimAdminLogin.request("post", resource, self.body, self.header)
        Assertions().assert_equal_value(response["status_code"],200)
        return self.BimAdminLogin

class Center:
    '''
    Center CAS登录类
    '''
    def __init__(self,centerusername,centerpassword,envConf,global_cache):
        self.cache = global_cache
        self.productId = envConf['centerProductid']
        self.username = centerusername
        self.password = centerpassword
        self.header = envConf["headers"]["plain_header"]
        self.CenterLogin = base_requests.Send(envConf['pds'], envConf, global_cache=self.cache)

    def getServerUrl(self):
        '''
        获取服务器地址信息
        '''
        resource = '/rs/centerLogin/serverurl'
        response = self.CenterLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"],200)
        assert len(response["serverURL"]) != 0
        for server in response["serverURL"]:
            number = response["serverURL"].index(server)
            self.cache.set(response["serverName"][number],response["serverURL"][number])

    def getDeployType(self):
        '''
        获取部署类型
        :return:
        '''
        resource = '/rs/centerLogin/deployType'
        response = self.CenterLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        deployType = response["Response_body"]
        self.cache.set('deployType', deployType)

    def getLT(self):
        '''
        获取LT
        :return:
        '''
        resource = '/login'
        response = self.CenterLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        html = response["Response_body"]
        pattern = 'value="LT(.+?)" />'
        lt = re.findall(pattern, html)[0]
        return lt

    def getTGC(self):
        '''
        获取TGC，依赖getLT接口
        :return:
        '''
        resource = '/login'#?service=+serverlist[6]["serverURL"].replace("://","%3A%2F%2F")
        body = f'_eventId=submit&execution=e1s1&lt=LT{self.getLT()}&password={self.password}&productId={self.productId}&submit=%25E7%2599%25BB%25E5%25BD%2595&username={self.username}'
        response = self.CenterLogin.request('post', resource, body, self.header)
        assert response["status_code"] == 200

    def getCompanyList(self):
        '''
        获取企业id列表
        :return:
        '''
        resource = "/rs/centerLogin/companyList"
        body = {"password": self.password,"username": self.username}
        response = self.CenterLogin.request('post', resource, body)
        Assertions().assert_equal_value(response["status_code"], 200)
        if len(response["epid"]) > 0:
            self.cache.set('CenterEpid',response["epid"][0])

    def switchCompany(self):
        '''
        切换到指定企业，依赖getCompanyList接口
        :return:
        '''
        resource = "/rs/centerLogin/login"
        body = {"epid":self.cache.get("CenterEpid",False),"password": self.password,"username": self.username}
        response = self.CenterLogin.request('post', resource, body)
        Assertions().assert_equal_value(response["status_code"], 200)

    def login(self):
        '''
        Center登录
        :return:
        '''
        self.getServerUrl()
        self.getDeployType()
        self.getTGC()
        self.getCompanyList()
        self.switchCompany()

class IworksApp:
    '''
    BV CAS登录类
    '''
    def __init__(self,username,password,envConf,global_cache):
        self.cache = global_cache
        self.productId = envConf['iworksAppProductId']
        self.username = username
        self.password = password
        self.header = envConf["headers"]["plain_header"]
        self.clientVersion = envConf["iworksApp"]["clientVersion"]
        self.casLogin = base_requests.Send(envConf['pds'], envConf, global_cache=self.cache)
        self.epid = ''

    def getServerUrl(self):
        '''
        获取服务器地址信息
        '''
        resource = '/rs/casLogin/serverUrl'
        response = self.casLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        assert len(response["serverURL"]) != 0
        for server in response["serverURL"]:
            number = response["serverURL"].index(server)
            self.cache.set(response["serverName"][number],response["serverURL"][number])

    def getLT(self):
        '''
        获取LT
        :return:
        '''
        resource = '/login'
        response = self.casLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        html = response["Response_body"]
        pattern = 'value="LT(.+?)" />'
        lt = re.findall(pattern, html)[0]
        return lt

    def getTGC(self):
        '''
        获取TGC，依赖getLT接口
        :return:
        '''
        resource = '/login'#?service=+serverlist[6]["serverURL"].replace("://","%3A%2F%2F")
        body = f'_eventId=submit&execution=e1s1&lt=LT{self.getLT()}&password={self.password}&productId={self.productId}&submit=%25E7%2599%25BB%25E5%25BD%2595&username={self.username}'
        response = self.casLogin.request('post', resource, body, self.header)
        Assertions().assert_equal_value(response["status_code"],200)

    def getCompanyList(self):
        '''
        获取企业id列表
        :return:
        '''
        resource = "/rs/casLogin/companyList"
        body = {"password": self.password,"userName": self.username, "clientVersion": self.clientVersion,
         "phoneModel": "国行(A1865)、日行(A1902)iPhone X", "platform": "ios", "innetIp": "192.168.7.184", "productId": self.productId,
         "token": "f54d6c8c13445a723a2863a72d460e5aec48010560ea2351bda6474de5164899", "systemVersion": "13.5.1",
         "hardwareCodes": "3465192946d57f13482640578c77ffa77d1f66a4"}
        response = self.casLogin.request('post', resource, body)
        Assertions().assert_equal_value(response["status_code"], 200)
        if len(response["enterpriseId"]) > 0:
            self.cache.set('iworksAppEpid', response["enterpriseId"][0])
            self.epid = response["enterpriseId"][0]
            return self.epid

    def switchCompany(self):
        '''
        切换到指定企业
        :return:
        '''
        resource = f"/rs/casLogin/changeEnterprise/{self.epid}"
        response = self.casLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)

    def login(self):
        '''
        登录BV CAS流程方法
        :return:
        '''
        self.getServerUrl()
        self.getTGC()
        self.getCompanyList()
        self.switchCompany()

class Iworks:
    '''
    iWorks CAS登录类
    '''
    def __init__(self,username,password,envConf,global_cache):
        self.cache = global_cache
        # self.rf = ManageConfig().getConfig(self.section)
        # self.wf = ManageConfig()
        self.productId = envConf['iWorksProductId']
        self.username = username
        self.password = password
        self.header =envConf["headers"]["soap_header"]
        self.header1 = envConf["headers"]["urlencoded_header"]
        self.casLogin = base_requests.Send(envConf['pds'], envConf, global_cache=self.cache)
        self.epid = ''

    def getServerUrl(self):
        '''
        获取服务器地址信息
        '''
        resource ='/webservice/lbws/casLoginService'
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:SASS="http://login.webservice.login.sso.lubansoft.com/">
    <SOAP-ENV:Body>
        <SASS:getServUrl/>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''
        response = self.casLogin.request('post',resource,body)
        Assertions().assert_equal_value(response["status_code"], 200)
        convertedXml = xmltodict.parse(response['Response_body'])
        Response_serverURL= base_utils.ResponseData(convertedXml)['soap:Envelope_soap:Body_ns2:getServUrlResponse_return_list'][0]
        assert len(Response_serverURL)!=0
        for server in Response_serverURL:
            self.cache.set(dict(server)["serverName"],dict(server)["serverURL"])

    def getLT(self):
        '''
        获取LT
        :return:
        '''
        resource = '/login'
        response = self.casLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        html = response["Response_body"]
        pattern = 'value="LT(.+?)" />'
        lt = re.findall(pattern, html)[0]
        return lt

    def getTGC(self):
        '''
        获取TGC，依赖getLT接口
        :return:
        '''
        resource = '/login'#?service=+serverlist[6]["serverURL"].replace("://","%3A%2F%2F")
        body = f'_eventId=submit&execution=e1s1&lt=LT{self.getLT()}&password={self.password}&productId={self.productId}&submit=%25E7%2599%25BB%25E5%25BD%2595&username={self.username}'
        response = self.casLogin.request('post',resource,body,self.header1)
        Assertions().assert_equal_value(response["status_code"],200)

    def getCompanyList(self):
        '''
        获取企业id列表
        :return:
        '''
        resource = "/webservice/lbws/casLoginService"
        body = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:log="http://login.webservice.login.sso.lubansoft.com/">
    <soapenv:Header/>
    <soapenv:Body>
        <log:getCompanyList/>
    </soapenv:Body>
</soapenv:Envelope>'''
        response = self.casLogin.request('post',resource,body)
        Assertions().assert_equal_value(response["status_code"], 200)
        convertedXml = xmltodict.parse(response['Response_body'])
        enterpriseId = base_utils.ResponseData(convertedXml)['soap:Envelope_soap:Body_ns2:getCompanyListResponse_return_enterpriseId']
        print(enterpriseId)
        if len(enterpriseId) > 0:
            epids = eval(json.dumps(enterpriseId))[0]
            self.cache.set('epid', epids)
            self.epid = epids
            return self.epid

    def switchCompany(self):
        '''
        切换到指定企业
        :return:
        '''
        resource = f"/rs/casLogin/changeEnterprise/{self.epid}"
        response = self.casLogin.request('get',resource)
        Assertions().assert_equal_value(response["status_code"], 200)

    def casLoginService(self):
        '''
        登录获取权限码（cas）casLogin(登录cas)
        :return:
        '''
        resource = "/webservice/lbws/casLoginService"
        body = f'''
       <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:log="http://login.webservice.login.sso.lubansoft.com/">
    <soapenv:Header/>
    <soapenv:Body>
        <log:casLogin>
            <!--Optional:-->
            <param>
                <!--Optional:-->
                <!--Optional:-->
                <epid>{self.epid}</epid>
                <!--Optional:-->
                <hardwareCodes>eb4af7830e478a6191b38f7687a81e81-f6d5e226a50d8a7ff4cd47252efaa128</hardwareCodes>
                <!--Optional:-->
                <!--Optional:-->
                <innetIp>172.16.21.147</innetIp>
                <platform>pc64</platform>
                <version>1.0.0</version>
            </param>
        </log:casLogin>
    </soapenv:Body>
</soapenv:Envelope>
'''
        response = self.casLogin.request('post',resource,body,self.header)
        Assertions().assert_equal_value(response["status_code"], 200)
        convertedXml = xmltodict.parse(response['Response_body'])
        Response_authCodes = base_utils.ResponseData(convertedXml)['soap:Envelope_soap:Body_ns2:casLoginResponse_return_clientAuthGroupResultList_list']
        print(Response_authCodes)
    def login(self):
        '''
        登录BV CAS流程方法
        :return:
        '''
        self.getServerUrl()
        self.getTGC()
        self.getCompanyList()
        self.casLoginService()

class IworksWeb:
    '''
    iworks web 登录类
    '''
    def __init__(self,username,password,envConf,global_cache):
        self.cache = global_cache
        self.productId = envConf['iworksWebProductId']
        self.username = username
        self.password = password
        self.header = envConf["headers"]["json_header"]
        self.casLogin = base_requests.Send(envConf['pds'], envConf, global_cache=self.cache)
        self.epid = ''

    def getServerUrl(self):
        '''
        获取服务器地址信息
        '''
        resource = '/rs/casLogin/serverUrl'
        response = self.casLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        assert len(response["serverURL"]) != 0
        for server in response["serverURL"]:
            number = response["serverURL"].index(server)
            self.cache.set(response["serverName"][number],response["serverURL"][number])

    def getTGC(self):
        '''
        获取TGT
        :return:
        '''
        resource = '/rs/v2/tickets/tgt?'
        body = {"password": self.password,"username": self.username,"productId":self.productId}
        response = self.casLogin.request('post', resource, body, self.header)
        Assertions().assert_equal_value(response["status_code"],200)

    def getCompanyList(self):
        '''
        获取企业id列表
        :return:
        '''
        resource = "/rs/v2/casLogin/listCompany"
        response = self.casLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        if len(response["data_enterpriseId"]) > 0:
            self.cache.set('iworksWebEpid', response["data_enterpriseId"][0])
            self.epid = response["data_enterpriseId"][0]
            return self.epid

    def switchCompany(self):
        '''
        切换到指定企业
        :return:
        '''
        resource = f"/rs/casLogin/casLogin"
        body = {"epid": self.epid}
        response = self.casLogin.request('post', resource,body)
        Assertions().assert_equal_value(response["status_code"], 200)

    def enterpriseInfo(self):
        '''
        获取企业信息
        :return:
        '''
        resource = f"/rs/casLogin/enterpriseInfo"
        response = self.casLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)

    def authgroup(self):
        '''
        获取授权
        :return:
        '''
        resource = f"/rs/v2/casLogin/authgroup/{self.productId}"
        response = self.casLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)

    def get_openapitoken(self):
        '''
        获取opnapi的token
        '''
        resource = f'/rs/v2/casLogin/openapi/token'
        response = self.casLogin.request('get', resource)
        if response["code"][0] == 200:
            self.cache.set('openapitoken', response["data"][0])
        Assertions().assert_all_code(response,200,200)

    def login(self):
        '''
        iworks web流程方法
        :return:
        '''
        self.getServerUrl()
        self.getTGC()
        self.getCompanyList()
        self.switchCompany()
        self.enterpriseInfo()
        self.authgroup()
        self.get_openapitoken()

class OpenAPI:
    '''
    开放平台登录类
    '''
    def __init__(self,apikey,apisecret,envConf,global_cache):
        self.cache = global_cache
        self.apikey = apikey
        self.apisecret = apisecret
        self.username = envConf["openapi"]['username']
        self.OpenAPIToken = base_requests.Send(envConf["openapi"]['host'], envConf, global_cache=self.cache)

    def login(self):
        '''
        登录获取token
        '''
        resource = f"/rs/token/{self.apikey}/{self.apisecret}/{self.username}"
        response = self.OpenAPIToken.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        # 获取到响应的token并更新到header中
        header = json.loads(self.OpenAPIToken.header)
        header.update({"token": response["data"][0]})
        self.OpenAPIToken.header = json.dumps(header)
        return self.OpenAPIToken


class Bimapp:
    '''
    Bimapp 登录类
    '''
    def __init__(self,username,password,envConf,global_cache):
        self.cache = global_cache
        self.username = base_utils.ToBase64(username)
        self.password = password
        self.token = ''
        self.AcAddress = ''
        self.BimappLogin = base_requests.Send(envConf["bimapp"]['host'], envConf, global_cache=self.cache)

    def getCookie(self):
        '''
        获取cookie
        '''
        resource = "/login.htm"
        response = self.BimappLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)

    def getAcAddress(self):
        '''
        获取ac地址
        '''
        resource = "/getAcAddress.htm"
        response = self.BimappLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        if response["Response_body"] is not None:
            self.AcAddress = response["Response_body"]

    def gettoken(self):
        '''
        获取token
        '''
        resource = f"{self.AcAddress}/rs/rest/user/login/{self.username}/{self.password}"
        response = self.BimappLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)
        self.token = response['loginToken'][0]

    def doLoginWithToken(self):
        '''
         token登录
        '''
        resource = f"/bimapp/doLoginWithToken.htm?token={self.token}"
        response = self.BimappLogin.request('get', resource)
        Assertions().assert_equal_value(response["status_code"], 200)


    def login(self):
        '''
        登录
        '''
        self.getCookie()
        self.getAcAddress()
        self.gettoken()
        self.doLoginWithToken()
        return self.BimappLogin


class MylubanWeb:
    '''
    MylubanWeb 登录类
    '''
    def __init__(self,username,password,envConf,global_cache):
        self.cache = global_cache
        self.username = username
        self.password = password
        self.MylubanWebLogin = base_requests.Send(envConf["MylubanWeb"]['host'], envConf, global_cache = self.cache)

    def login(self):
        '''
        MylubanWeb登录
        :param MylubanWebLogin:
        :return:
        '''
        resource = "/myluban/rest/login"
        body = {"username":self.username,"password":self.password}
        response = self.MylubanWebLogin.request('post', resource, body)
        Assertions().assert_equal_value(response["status_code"], 200)
        return self.MylubanWebLogin

class Bussiness:
    '''
    Bussiness 登录类
    '''
    def __init__(self,username,password,envConf,global_cache):
        self.cache = global_cache
        self.username = username
        self.password = password
        self.BussinessLogin = base_requests.Send(envConf["Bussiness"]['host'], envConf, global_cache = self.cache)

    def login(self):
        '''
        Bussiness 登录
        :param BussinessLogin:
        :return:
        '''
        resource = "/login"
        body = {"username":self.username,"password":self.password}
        response = self.BussinessLogin.request('post', resource, body)
        Assertions().assert_equal_value(response["status_code"], 200)
        return self.BussinessLogin

class LubanSoft:
    '''
    lubansoft 登录类
    '''
    def __init__(self,username,password,envConf,global_cache):
        self.cache = global_cache
        self.username = username
        self.password = password
        self.header = envConf["headers"]["soap_header"]
        self.lubansoftLogin = base_requests.Send(envConf["lubansoft"]['host'], envConf)

    def login(self):
        '''
        lubansoft 登录
        :return:
        '''
        resource = "/login"
        body = '''<?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xop="http://www.w3.org/2004/08/xop/include" xmlns:ns1="http://cloudnorm.webservice.lbapp.lubansoft.com/" xmlns:ns10="http://webservice.clientcomponent.lbapp.lubansoft.com/" xmlns:ns11="http://webservice.cloudcomponent.lbapp.lubansoft.com/" xmlns:ns12="http://webservice.lbim.lbapp.lubansoft.com/" xmlns:ns13="http://webservice.common.lbapp.lubansoft.com/" xmlns:ns14="http://webservice.costlib.lbapp.lubansoft.com/" xmlns:ns15="http://webservice.usergrade.lbapp.lubansoft.com/" xmlns:ns16="http://webservice.cloudautoset.lbapp.lubansoft.com/" xmlns:ns17="http://webservice.lbcert.lbapp.lubansoft.com/" xmlns:ns18="http://webservice.clientinfo.lbapp.lubansoft.com/" xmlns:ns19="http://webservice.onlineservice.lbapp.lubansoft.com/" xmlns:ns2="http://lbmsg.webservice.lbapp.lubansoft.com/" xmlns:ns20="http://webservice.localbim.lbapp.lubansoft.com/" xmlns:ns21="http://webservice.adimage.lbapp.lubansoft.com/" xmlns:ns22="http://webservice.banbankDrainage.lbapp.lubansoft.com/" xmlns:ns3="http://upgrade.webservice.lbapp.lubansoft.com/" xmlns:ns4="http://cloudpush.webservice.lbapp.lubansoft.com/" xmlns:ns5="http://common.webservice.lbapp.lubansoft.com/" xmlns:ns6="http://clientInfo.webservice.lbapp.lubansoft.com/" xmlns:ns7="http://validate.webservice.lbapp.lubansoft.com/" xmlns:ns8="http://LBUFS.webservice.lbapp.lubansoft.com/" xmlns:ns9="http://webservice.dataserver.LBUFS.lubansoft.com/">
        <SOAP-ENV:Header><LBTag>Kick</LBTag><LBSessionId></LBSessionId></SOAP-ENV:Header>
        <SOAP-ENV:Body>
        <ns6:login>
        <LBLoginParam>
        <computerName>DESKTOP-S2CJPRR</computerName>
        <hardwareCodes>0d80c194d531820c71de04a3998b435e-4ece03d1c7f03a151b241cbd455505ef</hardwareCodes>
        <intranet_IP>172.16.21.178</intranet_IP>
        <lubanNetVersion>4.9.0.5</lubanNetVersion>
        <password>96e79218965eb72c92a549dd5a330112</password>
        <platform>64</platform>
        <productId>3</productId>
        <softwareEnvironment>hostType=CAD;hostVer=2012;OSName=Windows 10;OSBit=64;OSVer=6-2;</softwareEnvironment>
        <username>hubiao</username>
        <version>30.2.1</version>
        </LBLoginParam>
        </ns6:login></SOAP-ENV:Body></SOAP-ENV:Envelope>'''
        response = self.lubansoftLogin.request('post', resource, body)
        Assertions().assert_equal_value(response["status_code"], 200)
        return self.lubansoftLogin

if __name__ == '__main__':
    pass"""

SWAGGER_DEMO = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2019/5/9 21:24
# @Author  : hubiao
# @File    : org_controller.py

import allure

class Org:
    '''
    组织机构、项目部相关接口
    '''
    @allure.step("查询组织机构树（包括项目部）")
    def org_nodes(self,CenterBuilder):
        '''
        查询组织机构树（包括项目部）
        '''
        resource = '/org/nodes'
        response = CenterBuilder.request('get', resource)
        return response

    @allure.step("创建新的组织机构")
    def org_orgId_add(self, CenterBuilder,orgId,orgName,dataType=1,type=0):
        '''
        创建新的组织机构
        orgId：组织机构节点ID
        orgName：创建的组织机构名称
        dataType：数据类型,1、组织数据类型2、项目部门数据类型
        type：组织类型 0:分公司,2:部门(已废弃)
        '''
        resource = f'/org/{orgId}/subs'
        body = {
            "name": orgName,
            "remarks": orgName+"的备注",
            "labels": [],
            "latitude": "121.517675",
            "longitude": "31.312552",
            "dataType":dataType,
            "type": type
        }
        response = CenterBuilder.request('post', resource, body)
        return response

    @allure.step("编辑组织机构")
    def org_orgId_edit(self, CenterBuilder,orgId,orgName):
        '''
        编辑组织机构
        orgId：组织机构节点ID
        orgName：创建的组织机构名称
        '''
        resource = f'/org/{orgId}'
        body = {
            "labels": [],
            "latitude": "121.517675",
            "longitude": "31.312552",
            "name": orgName,
            "remarks": orgName+"的备注"
        }
        response = CenterBuilder.request('put', resource, body)
        return response

    @allure.step("删除组织机构、项目部")
    def org_orgId_del(self, CenterBuilder,orgId):
        '''
        删除组织机构
        orgId：组织机构节点ID
        '''
        resource = f'/org/{orgId}'
        response = CenterBuilder.request('delete', resource)
        return response"""

CASE_DEMO = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2019/5/13 17:12
# @Author  : hubiao
# @File    : test_center_demo.py

import pytest
import allure
from luban_common.base_assert import Assertions
from swagger.builder.org import Org
from luban_common import base_utils


@allure.feature("组织机构、项目部")
class TestOrg:
    '''
    组织机构、项目部相关接口
    '''

    def setup_class(self):
        '''
        定义接口需要用到的字段信息
        '''
        pass

    @allure.story("组织机构")
    @allure.title("编辑组织机构")
    @pytest.mark.parametrize("dataType", [1,2])
    def test_org_edit(self, center_builder, dataType):
        '''
        编辑组织机构接口测试
        '''
        # 查询组织机构树
        response = Org().org_nodes(center_builder)
        rootID = response["result_id"][response["result_root"].index(True)]
        # 创建组织机构
        orgName = '接口测试新增机构' + base_utils.generate_random_str()
        org_add = Org().org_orgId_add(center_builder, rootID, orgName=orgName, dataType=dataType)
        org_id = org_add["result_id"][0]
        org_pathId = org_add["result_pathId"][0]
        org_path = org_add["result_path"][0]
        # 编辑组织机构
        newOrgName = '接口测试编辑机构' + base_utils.generate_random_str()
        org_edit = Org().org_orgId_edit(center_builder, orgId=org_id, orgName=newOrgName)
        # 查询组织机构树
        response = Org().org_nodes(center_builder)
        try:
            Assertions().assert_all_code(response, 200, 200)
            # 验证编辑组织接口是否正常
            Assertions().assert_equal_value(org_edit["result_id"][0],org_id)
            Assertions().assert_equal_value(org_edit["result_name"][0],newOrgName)
            Assertions().assert_equal_value(org_edit["result_type"][0],0)
            Assertions().assert_equal_value(org_edit["result_parentId"][0],rootID)
            Assertions().assert_equal_value(org_edit["result_root"][0],False)
            Assertions().assert_equal_value(org_edit["result_dataType"][0],dataType)
            # 验证组织树接口是否返回了新加的组织
            Assertions().assert_in_value(response["result_id"],org_id)
            Assertions().assert_equal_value(response["result_name"][response["result_id"].index(org_id)],newOrgName)
            Assertions().assert_equal_value(response["result_type"][response["result_id"].index(org_id)],0)
            Assertions().assert_equal_value(response["result_parentId"][response["result_id"].index(org_id)],rootID)
            Assertions().assert_equal_value(response["result_root"][response["result_id"].index(org_id)],False)
            Assertions().assert_equal_value(response["result_pathId"][response["result_id"].index(org_id)],org_pathId)
            Assertions().assert_equal_value(response["result_path"][response["result_id"].index(org_id)],org_path)
            Assertions().assert_equal_value(response["result_dataType"][response["result_id"].index(org_id)],dataType)
        finally:
            # 删除组织机构
            Org().org_orgId_del(center_builder, orgId=org_id)


if __name__ == '__main__':
    pytest.main(["-s", "test_center_demo.py"])"""

class NewCommand(BaseCommand):
    """
    Create a new test project

    new
        {name : 测试项目的名称}
    """

    def handle(self):
        from pathlib2 import Path

        path = Path.cwd() / Path(self.argument("name"))
        name = self.argument("name")
        if not name:
            name = path.name

        if path.exists():
            if list(path.glob("*")):
                # Directory is not empty. Aborting.
                raise RuntimeError(
                    "Destination <fg=yellow>{}</> "
                    "exists and is not empty".format(path)
                )
        # 初始化 package
        packages = []
        packages.append(path / "testcases")
        packages.append(path / "testsuites")
        packages.append(path / "business")
        packages.append(path / "utils")
        packages.append(path / "swagger")
        packages.append(path / "swagger/builder")
        for package in packages:
            package.mkdir(mode=0o777, parents=True, exist_ok=False)
            package_init = package / "__init__.py"
            package_init.touch(exist_ok=False)
            self.line("Created packages: <fg=green>{}</>".format(package))

        # 初始化 folder
        folders = []
        folders.append(path / "config/dev")
        folders.append(path / "config/enterprise")
        folders.append(path / "config/preRelease")
        folders.append(path / "config/release")
        folders.append(path / "data")
        folders.append(path / "reports")
        for folder in folders:
            folder.mkdir(mode=0o777, parents=True, exist_ok=False)
            self.line("Created folder: <fg=green>{}</>".format(folder))

        # 初始化 conftest.py
        conftest_default = path / "conftest.py"
        with conftest_default.open("w", encoding="utf-8") as f:
            f.write(CONFTEST_DEFAULT)
            self.line("Created file: <fg=green>{}</>".format(conftest_default))

        # 初始化 utils.py
        utils_default = path / "utils/utils.py"
        with utils_default.open("w", encoding="utf-8") as f:
            f.write(UTILS_DEFAULT.format(name))
            self.line("Created file: <fg=green>{}</>".format(utils_default))

        # config 中初始化全局 yaml 配置文件
        globalconfig_default = path / "config/globalConf.yaml"
        with globalconfig_default.open("w", encoding="utf-8") as f:
            f.write(GLOBAL_CONFIG_DEFAULT)
            self.line("Created file: <fg=green>{}</>".format(globalconfig_default))

        # config 中初始化环境 yaml 配置文件
        for folder in folders[0:4]:
            config_default = folder / "config.yaml"
            with config_default.open("w", encoding="utf-8") as f:
                f.write(CONFIG_DEFAULT)
                self.line("Created file: <fg=green>{}</>".format(config_default))

        # 初始化 pytest.ini 配置文件
        pytestini_default = path / "pytest.ini"
        with pytestini_default.open("w", encoding="utf-8") as f:
            f.write(PYTESTINI_DEFAULT)
            self.line("Created file: <fg=green>{}</>".format(pytestini_default))

        # 初始化 .gitignore 文件
        git_default = path / ".gitignore"
        with git_default.open("w", encoding="utf-8") as f:
            f.write(GIT_DEFAULT)
            self.line("Created file: <fg=green>{}</>".format(git_default))

        self.line("Initializing .........")
        self.__init(path)
        self.line("initialization End")
        self.line("<fg=green>Successfully Created {}</>".format(name))

    def __init(self,path):
        # 初始化公共登录 public_login.py 文件
        public_login = path / "business/public_login.py"
        with public_login.open("w", encoding="utf-8") as f:
            f.write(PUBLIC_LOGIN)
            self.line("Created file: <fg=green>{}</>".format(public_login))
        # 初始化swagger org.py
        swagger_demo_default = path / "swagger/builder/org.py"
        with swagger_demo_default.open("w", encoding="utf-8") as f:
            f.write(SWAGGER_DEMO)
            self.line("Created file: <fg=green>{}</>".format(swagger_demo_default))
        # 初始化 test_center_demo.py 用例
        case_demo_default = path / "testsuites/test_center_demo.py"
        with case_demo_default.open("w", encoding="utf-8") as f:
            f.write(CASE_DEMO)
            self.line("Created file: <fg=green>{}</>".format(case_demo_default))