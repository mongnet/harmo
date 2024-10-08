#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by hubiao on 2017/5/9
from __future__ import print_function
import ast
import base64
import calendar
import hashlib
import hmac
import ipaddress
import os
import re
import secrets
import string
import uuid
import subprocess
import time
from urllib.parse import urlparse

import jsonpath
from datetime import datetime, timedelta
from typing import Union, Optional, List
from harmo.config import Config
from harmo import http_requests
from pathlib2 import Path
from bs4 import BeautifulSoup

def getFileMD5(file_Path: str) -> Optional[str]:
    '''
    传入文件路径，返回文件MD5
    :param file_Path: 文件路径，相对于项目根目录，如 data/Doc/Lubango20191205.docx
    :return: MD5值
    '''
    try:
        file = file_absolute_path(file_Path)
        with open(file, 'rb') as fileObjct:
            m = hashlib.md5()
            while True:
                d = fileObjct.read(4096)  # 每次读取4KB的数据
                if not d: break  # 如果读出来的数据为空时跳出循环
                m.update(d)
            return m.hexdigest()
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def getFileSize(file_Path: str) -> int:
    '''
    传入文件路径，返回文件大小
    :param file_Path: 文件路径，相对于项目根目录，如 data/Doc/Lubango20191205.docx
    :return: 文件大小
    '''
    file = file_absolute_path(file_Path)
    return os.path.getsize(file)

def getFileName(file_Path: str) -> str:
    '''
    传入文件路径，返回文件名称
    :param file_Path: 文件路径，相对于项目根目录，如 data/Doc/Lubango20191205.docx
    :return: 文件名
    '''
    file = file_absolute_path(file_Path)
    return os.path.basename(file)

def file_is_exist(file_path: str) -> str:
    '''
    判断文件是否存在
    :param file_path:
    :return:
    '''
    new_path = Path(os.path.normpath(file_path).replace('\\', '/')) if os.sep == '/' else Path(os.path.normpath(file_path))
    if not new_path.exists():
        raise FileNotFoundError(f"请确认 {new_path} 文件路径是否正确！")
    return os.path.abspath(new_path)

def file_absolute_path(rel_path: str) -> str:
    '''
    通过文件相对路径，返回文件绝对路径
    :param rel_path: 相对于项目根目录的路径，如data/check_lib.xlsx
    :return:
    '''
    new_path = Path(os.path.normpath(rel_path).replace('\\', '/')) if os.sep == '/' else Path(os.path.normpath(rel_path))
    if os.path.isfile(new_path):
        return os.path.abspath(new_path)
    _current_path = Config.project_root_dir  # os.path.abspath(os.path.dirname(__file__))
    _file_path = os.path.join(_current_path, new_path)
    return file_is_exist(_file_path)

def getStrMD5(String: str) -> str:
    '''
    传入一个字符串，返回字符串MD5值
    :param String: 字符串
    :return: MD5值
    '''
    if not isinstance(String, str):
        String = str(String)
    m = hashlib.md5()
    m.update(String.encode('utf-8'))
    return m.hexdigest()

def getStrSha1(String: str) -> str:
    """
    sha1 算法加密
    :param msg: 需加密的字符串
    :return: 加密后的字符
    """
    if not isinstance(String, str):
        String = str(String)
    sh = hashlib.sha1()
    sh.update(String.encode('utf-8'))
    return sh.hexdigest()

def ToBase64(String: str) -> str:
    '''
    传入一个字符串，返回字符串的Base64
    :param String: 字符串
    :return: 返回Base64编码
    '''
    if not isinstance(String, str):
        String = str(String)
    base64Str = base64.urlsafe_b64encode(String.encode("utf-8"))
    return str(base64Str, 'utf-8')

def FromBase64(String: str) -> str:
    '''
    传入一个Base64，返回字符串
    :param String: 字符串
    :return: 返回字符串
    '''
    if not isinstance(String, str):
        String = str(String)
    missing_padding = 4 - len(String) % 4
    if missing_padding:
        String += '=' * missing_padding
    return str(base64.urlsafe_b64decode(String), 'utf-8')

def toFileBase64(file_path: str) -> str:
    '''
    传入一个文件，返回文件的Base64编码
    :param file_path: 文件
    :return: 返回Base64编码
    '''
    file = file_absolute_path(file_path)
    with open(file, 'rb') as f:
        image = f.read()
    return str(base64.b64encode(image), encoding='utf-8')

def getUnix(date: str = None, day: int = 0, current: bool = True, scope: str = "s") -> int:
    '''
    通过传入的时间获取时间戳，默认获取当前时间戳
    :param date:传入的时间，格式为：'2017-05-09 18:31:22'，当传的格式为'2017-05-09'时会自动转换成'2017-05-09 23:59:59'
    :param day:时间差，只能为正负整数，比如要向后推2天时，day可传2
    :param current: 是否当前时间，True:当前时间，False:当天23:59:59
    :param scope:时间戳范围，s(秒)，其它情况为(毫秒)
    :return: 返回时间戳
    '''
    if not isinstance(day, int):
        raise ValueError("day参数只能为整数")
    if date is None:
        ST = time.strptime(str(datetime.now() + timedelta(days=day))[:19],
                           "%Y-%m-%d %H:%M:%S") if current else time.strptime(
            str(datetime.now() + timedelta(days=day))[:10] + " 23:59:59", "%Y-%m-%d %H:%M:%S")
    else:
        if not isinstance(date, str):
            raise ValueError("date参数只能为字符串")
        if len(date) == 19:
            ST = time.strptime(str(datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(days=day)),
                               "%Y-%m-%d %H:%M:%S")
        elif len(date) == 10:
            ST = time.strptime(str(datetime.strptime(date + " 23:59:59", "%Y-%m-%d %H:%M:%S") + timedelta(days=day)),
                               "%Y-%m-%d %H:%M:%S")
        else:
            raise ValueError("date 只能为10位'2017-05-09'或19位'2017-05-09 23:59:59'的字符串")
    unixST = int(time.mktime(ST)) if scope == "s" else int(time.mktime(ST)) * 1000
    return unixST

def UnixToTime(unix: int) -> str:
    '''
    把时间戳转换成时间
    :param unix: 时间戳
    :return: 返回时间
    '''
    if not isinstance(unix, int):
        raise TypeError("时间戳只能是整型")
    if len(str(unix)) == 13:
        time_local = time.localtime(int(unix) / 1000)
    elif len(str(unix)) == 10:
        time_local = time.localtime(int(unix))
    else:
        raise ValueError("传入参数错误，不是一个正确的时间戳，正确时间戳应该为10或13位")
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def getRecentMonthOfDay():
    '''
    获取近一个月的开始时间,比如今天是2016-12-15 12:25:00，那么返回的时间为2016-11-15 00:00:00
    :return: 返回最近一个月的开始时间
    '''
    d = datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    year = d.year
    month = d.month

    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    days = calendar.monthrange(year, month)[1]
    # 上月同一天00:00到当前这一刻，认定为最近一月，如果要为上一天数据days减1即可
    day = d - timedelta(days=days)
    unixtime = int(time.mktime(day.timetuple())) * 1000
    return unixtime, day

def calday(month: int, year: int):
    '''
    根据指定的年月，返回当月天数
    :param month: 月份
    :param year: 年份
    :return: 返回指定年月当月天数
    '''
    if not isinstance(month, int) and not isinstance(year, int):
        raise TypeError("只支持整型")
    elif not (month >= 1 and month <= 12):
        raise SyntaxError("月份只能在1到12之间")
    elif not year > 0:
        raise SyntaxError("年份不能小于0")
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        days = "31"
        return days
    elif month == 4 or month == 6 or month == 9 or month == 11:
        days = "30"
        return days
    elif month == 2:
        if calendar.isleap(year):
            days = "29"
            return days
        else:
            days = "28"
            return days

def shell(cmd):
    '''
    CMD命令执行函数
    :param cmd: 执行的命令
    :return: 返回执行结果
    '''
    output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    o = output.decode("utf-8")
    return o

def generate_random_str(randomlength: int = 8) -> str:
    '''
    生成随机字符串
    :param randomlength: 默认生成的字符串长度为8位
    :return: 返回随机字符串
    '''
    return "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(randomlength))

def generate_random_mail() -> str:
    '''
    生成随机邮件地址
    :return: 返回随机邮件地址
    '''
    postfix = ["163.com", "126.com", "qq.com", "yahoo.com.cn"]
    return generate_random_str() + "@" + secrets.choice(postfix)

def generate_random_mobile() -> str:
    '''
    生成随机手机号
    :return:
    '''
    prefix = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
              "141", "145", "146", "147", "150", "151", "152", "153", "155", "156", "157", "158", "159", "166",
              "170", "172", "173", "174", "176", "177", "178", "180", "181", "182", "183", "184", "185", "186", "187",
              "188", "189",
              "191","198", "199"]
    return secrets.choice(prefix) + ''.join(secrets.choice(string.digits) for _ in range(8))

def generate_random_serial_numbers(length: int,num: int) -> list:
    """
    生成随机流水号
    :param length: 流水号长度
    :param num: 流水号数量
    :return: 包含 num 个长度为 length 的随机数字列表
    """
    if length <= 0:
        raise ValueError("流水号长度必须大于0。")
    if num <= 0:
        raise ValueError("流水号数量必须大于0。")
    random_digits = []
    for _ in range(num):
        # 生成一个指定长度的随机数字字符串
        random_number = ''.join(secrets.choice(string.digits) for _ in range(length))
        random_digits.append(random_number)
    return random_digits

def dict_generator(indict, pre=None):
    '''
    字典生成器
    :param indict:
    :param pre:
    :return:
    '''
    try:
        pre = pre[:] if pre else []
        if isinstance(indict, dict):
            for key, value in indict.items():
                if isinstance(value, dict):
                    if len(value) == 0 and pre == []:
                        yield pre + [key, {}]
                    elif len(value) == 0 and pre != []:
                        yield ["_".join(pre) + '_' + key, {}]
                    else:
                        for d in dict_generator(value, pre + [key]): yield d
                elif isinstance(value, list):
                    if len(value) == 0 and pre == []:
                        yield pre + [key, []]
                    elif len(value) == 0 and pre != []:
                        yield ["_".join(pre) + '_' + key, []]
                    else:
                        yield ["_".join(pre) + '_' + key + '_list', value]
                        for v in value:
                            for d in dict_generator(v, pre + [key]): yield d
                elif isinstance(value, tuple):
                    if len(value) == 0 and pre == []:
                        yield pre + [key, ()]
                    elif len(value) == 0 and pre != []:
                        yield ["_".join(pre) + '_' + key, ()]
                    else:
                        for v in value:
                            for d in dict_generator(v, pre + [key]): yield d
                else:
                    if pre != []:
                        yield ["_".join(pre) + '_' + key, value]
                    else:
                        yield [key, value]
        elif isinstance(indict, list):
            for values in indict:
                for d in dict_generator(values):
                    yield d
        else:
            if pre != []: yield ["_".join(pre), indict]
    except BaseException as e:
        print(str(e))

def ResponseData(indict):
    '''
    通过数据生成字典
    :param indict:
    :return:
    '''
    try:
        templist, result, key = [], {}, []
        try:
            for i in dict_generator(indict): templist.append(i)
        except:
            pass
            # for i in dict_generator(eval(json.dumps(dict(xmltodict.parse(data))))):templist.append(i)
        for value in templist: key.append(value[0])
        for keys in list(set(key)):
            result[keys] = []
            for values in templist:
                if keys == values[0]: result[keys].append(values[1])
        result["source_response"] = indict
        return result
    except BaseException as e:
        print(str(e))

def Search_html_tag(url: str, label: str, matchText: str, attribute=None) -> list:
    '''
    请求网页并搜索指定的html标签或属性内是否有指定文本
    :param url: 指定要检查的连接地址
    :param label: 指定要检查的html或xml标签，不要尖括号，如:h2
    :param matchText: 指定要检查是否存在的文本
    :param attribute: html属性，如：<script src="./static/iconfont.js"> 中的 src
    :return:
    '''
    try:
        # 请求服务器
        req = http_requests.HttpRequests(url)
        resp = req.send_request("GET", url).get("response_obj")
    except BaseException as e:
        assert False, f'请求连接地址出错，错误信息为:{e}'
    # 查询指定标签
    bsObj = BeautifulSoup(resp.text,"html.parser")
    # 判断是否找到指定标签
    namelist = bsObj.findAll(label)
    result = []
    for name in namelist:
        # 判断标签中的值是否为指定的文本
        try:
            if attribute:
                text = name[attribute]
            else:
                text = name.__str__()
            if text.__contains__(matchText):
                result.append(text)
        except KeyError:
            pass
    return result

def TextLineContains(url, textKey, textValue, split_str_list: Optional[list]=None, **kwargs):
    '''
    文本行是否包含指定文本
    :param url: 指定要检查文件连接地址
    :param textKey: 检查文本key
    :param textValue: 检查文本Value
    :param split_str_list: 分割字符串列表，默认为空
    :return: None:不包含textKey,1:不包含textValue,2:包含textKey和textValue
    '''
    # 请求服务器
    req = http_requests.HttpRequests(url)
    resp = req.send_request("GET", url, **kwargs)
    from harmo.base_assert import Assertions
    Assertions.assert_code(resp, resp.get("status_code"), 200)
    # 按行循环
    for line in resp.get("response_obj").text.splitlines():
        # 清除空格
        textLine = line.strip()
        if isinstance(split_str_list,list):
            for split_str in split_str_list:
                for comma in textLine.split(f"{split_str}"):
                    if not comma.startswith("/") and comma.isprintable() and comma:
                        if comma.__contains__(textKey):
                            if comma.__contains__(textValue):
                                return 2, comma
                            else:
                                return 1, comma
        else:
            if not textLine.startswith("/") and textLine.isprintable() and textLine:
                if textLine.__contains__(textKey):
                    if textLine.__contains__(textValue):
                        return 2, textLine
                    else:
                        return 1, textLine
    return None, None

def time_difference(start_time, end_time):
    '''
    获取时间差
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: 返回时间差(秒)
    '''
    if isinstance(start_time, datetime):
        return (end_time - start_time).seconds
    else:
        raise TypeError("只支持 datetime 类型")

def jpath(data, check_key, check_value=None, sub_key=None):
    '''
    jsonpath封装,例：jsonpath.jsonpath(data,$..[?(@.functionKey=='D-2')]..openStatus)
    :param data: 需要获取的数据,类型必须是dict,否侧返回False
    :param check_key: 检查key,例子中的functionKey
    :param check_value: 检查value,辅助定位,例子中的'D-2'
    :param sub_key: 检查子key,辅助定位,例子中的openStatus,当指定sub_key时,只返回sub_key对应的values,其它数据不返回
    :return: 匹配时返回对应list,否则返回False
    '''
    # if not isinstance(data,dict):
    #     return False
    if check_value is not None:
        if isinstance(check_value, int):
            expr = f"$..[?(@.{check_key}=={check_value})]" if sub_key is None else f"$..[?(@.{check_key}=={check_value})]..{sub_key}"
        elif isinstance(check_value, str):
            expr = f'$..[?(@.{check_key}=="{check_value}")]' if sub_key is None else f'$..[?(@.{check_key}=="{check_value}")]..{sub_key}'
        else:
            return False
    else:
        expr = f"$..[?(@.{check_key})]" if sub_key is None else f"$..[?(@.{check_key})]..{sub_key}"
    return jsonpath.jsonpath(data, expr)

def get_all_key(data: Union[dict,list], filter_key: Optional[List[str]]=None) -> list:
    '''
    获取全部字典的key，包含列表中包含的字典
    :param data:
    :return: key组成的列表，未去重
    '''
    ALLKEY = []
    def in_key(data):
        if isinstance(data, list):
            for item in data:
                in_key(item)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    in_key(value)
                if filter_key and key in filter_key:
                    pass
                else:
                    ALLKEY.append(key)
        return ALLKEY
    return in_key(data)

def get_all_value(data: Union[dict,list], filter_key: Optional[List[str]]=None) -> list:
    '''
    获取全部value，可取list和dict的value值
    :param data:
    :return: value组成的列表，未去重
    '''
    ALLVALUE = []
    def in_key(data):
        if isinstance(data, list):
            for item in data:
                if isinstance(item, (list, dict)):
                    in_key(item)
                else:
                    ALLVALUE.append(item)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    in_key(value)
                else:
                    if filter_key and key in filter_key:
                        pass
                    else:
                        ALLVALUE.append(value)
        return ALLVALUE
    return in_key(data)

def strListToList(string: str) -> list:
    '''
    字符串类型的列表转为列表
    :param string: "['1', '2', '3']" ---> ['1', '2', '3']
    :return: list
    '''
    return ast.literal_eval(string)

def gen_uuid(filter: bool = False) -> str:
    '''
    生成uuid
    :param filter: 生成的uuid默认会带有'-'，当filter为False时不过滤'-'，默认为False
    :return:
    '''
    if filter:
        uid = ''.join(str(uuid.uuid4()).split('-'))
    else:
        uid = uuid.uuid4()
    return uid

def gen_sign(timestamp, secret) -> str:
    '''
    根据时间戳和secret生成签名
    使用场景：请求数据时发送当前时间戳和生成的签名，接受方根据约定的secret和发送过来的时间戳，以相同方式获取签名，如生成的签名一致，表示签名有效
    :param timestamp: 时间戳
    :param secret: 秘钥
    :return: 签名
    '''
    if not timestamp or not secret:
        raise ValueError("timestamp 或 secret 不是一个有效的参数")
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return sign

def recursion_replace_dict_value(source: Union[dict,list], replaceDict: dict) -> None:
    '''
    递归替换字典，根据value值替换value的值
    example:
        source = {"ex": null,"state": false,"age": 38}
        replaceDict = {"null": None,"false": False}
        result = {"ex": None,"state": False,"age": 38}
    :param source: 需要替换的字典或字典组成的列表
    :param replaceDict: 要检查并替换的字段，key为要检查的值，value为需要替换的值
    :return: 没有返回值，直接修改source
    '''
    if not isinstance(replaceDict,dict):
        raise TypeError("replaceDict 必需是dict类型")
    if isinstance(source, list):
        for item in source:
            recursion_replace_dict_value(item,replaceDict)
    elif isinstance(source, dict):
        for key, value in source.items():
            if isinstance(value, dict) or isinstance(value, list):
                recursion_replace_dict_value(value, replaceDict)
            else:
                for checkValue, replaceValue in replaceDict.items():
                    if str(value) == str(checkValue):
                        source[key] = replaceValue
    else:
        pass

def recursion_replace_dict_key_value(source: Union[dict,list], replaceDict: dict) -> None:
    '''
    递归替换字典，根据key名替换key的值
    example:
        source = {"ex": null,"state": false,"age": 38}
        replaceDict = {"ex": None,"state": False}
        result = {"ex": None,"state": False,"age": 38}
    :param source: 需要替换的字典或字典组成的列表
    :param replaceDict: 要检查并替换的字段，key为要检查的key名，value为需要替换的值
    :return: 没有返回值，直接修改source
    '''
    if not isinstance(replaceDict,dict):
        raise TypeError("replaceDict 必需是dict类型")
    if isinstance(source, list):
        for item in source:
            recursion_replace_dict_key_value(item,replaceDict)
    elif isinstance(source, dict):
        for key, value in source.items():
            if isinstance(value, dict) or isinstance(value, list):
                recursion_replace_dict_key_value(value, replaceDict)
            else:
                for checkey, replaceValue in replaceDict.items():
                    if str(key) == str(checkey):
                        source[key] = replaceValue
    else:
        pass

def coincide_list(lists: list) -> list:
    index = [len(v) for v in lists].index(min([len(v) for v in lists]))
    match =[]
    for i in range(len(lists[index])):
        switch =True
        for k in lists:
            if lists[index][i]!=k[i]:
                switch =False
        if switch:
            match.append(lists[index][i])
        else:
            break
    return match

def get_match_text(url, textKeys: List[str], split_str_list: Optional[list]=None, **kwargs) -> list:
    """
    获取匹配文本
    :param url: 请求地址
    :param textKeys: 匹配关键字
    :param split_str_list: 匹配关键字前需要分割的字符串列表
    :param kwargs:
    :return:
    """
    # 请求服务器
    req = http_requests.HttpRequests(url)
    resp = req.send_request("GET", url, **kwargs)
    from harmo.base_assert import Assertions
    Assertions.assert_code(resp, resp.get("status_code"), 200)
    match_list = []
    # 按行循环
    for line in resp.get("response_obj").text.splitlines():
        # 清除前后空格
        textLine = line.strip()
        if isinstance(split_str_list,list):
            for split_str in split_str_list:
                for comma in textLine.split(f"{split_str}"):
                    if not comma.startswith("/") and comma.isprintable() and comma:
                        for textKey in textKeys:
                            if comma.__contains__(textKey):
                                match_list.append(comma)
        else:
            if not textLine.startswith("/") and textLine.isprintable() and textLine:
                for textKey in textKeys:
                    if textLine.__contains__(textKey):
                        match_list.append(textLine)
    return match_list

def extract_urls(dataList: List[str]) -> list:
    '''
    从给定的字符串列表中提取所有URL地址。
    :param dataList: 包含URL的字符串列表。
    :return: 提取的URL列表
    '''
    # URL的正则表达式模式
    url_pattern = re.compile(r'http[s]?://[^"]+')
    # 用于存储所有找到的URL
    urls = []
    # 遍历数据，提取URL
    for item in dataList:
        # 对于列表中的每个元素，查找所有匹配的URL
        found_urls = url_pattern.findall(item)
        for url in found_urls:
            # 将找到的URL添加到列表中
            urls.append(url.strip().split('"')[0].split("'")[0])
    return urls

def is_private_ip(ip: str) -> bool:
    '''
    判断是否为私有IP地址
    :param ip:
    :return:
    '''
    private_ip_ranges = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('169.254.0.0/16')
    ]
    try:
        ip_addr = ipaddress.ip_address(ip)
        return any(ip_addr in private_ip for private_ip in private_ip_ranges)
    except ValueError:
        return False

def is_internal_url(url: str) -> bool:
    '''
    判断是否为内部URL
    :param url:
    :return:
    '''
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    if not hostname:
        return False
    return is_private_ip(hostname)

def is_valid_url(url) -> bool:
    """
    判断是否为有效的URL
    :param url:
    :return:
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def remove_adjacent_duplicates(lst) -> list:
    """
    从列表中删除相邻的重复项，不支持嵌套列表
    example:
        lst = [2222,2222,222.2,222.2,'project',2222, 'tree', 'Tree', 'comPonentdetail', 'Tree']
        result = ['2222', 222.2, 'project', 2222, 'tree', 'comPonentdetail', 'Tree']
    :param lst:
    :return:
    """
    if not isinstance(lst, list):
        raise TypeError("Input must be a list")
    iterator = iter(lst)
    last = str(next(iterator)).lower()
    yield last
    for item in iterator:
        item_str = str(item).lower()
        if item_str != last:
            yield item
            last = item_str

def extract_base_url(full_url):
    """
    提取URL的基地址
    example:
        full_url = "https://miao.baidu.com/abdr?_o=luban.cn"
        result = "https://miao.baidu.com"
    :param full_url:
    :return:
    """
    parsed_url = urlparse(full_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

if __name__ == "__main__":
    pass
    # dict1 = {"projId": 113692, "ppid": 130817, "projName": "BW接口用工程-勿删160711"}
    # dict2 = {"projId": 113692, "projName": "BW接口用工程-勿删160711", "ppid": 130817}
    # dict3 = {'hu': [1111, 'adfaf', '胡彪']}
    list1 = [['1111', 'adfaf','1111'],['1111','1111', 'adfaf', '胡彪']]
    print(coincide_list(list1))
    original_list = [2222,2222,222.2,222.2,'project',2222, 'tree', 'Tree', 'comPonentdetail', 'Tree', 'ppid', 'ppid']
    print(list(remove_adjacent_duplicates(original_list)))
    print(is_valid_url("http://192.168.13.172:19900:19900/auth/oauth2/logout"))
    # list2 = [1111, '胡彪', 'adfaf']
    # str2 = {'hu': 'adf'}
    # list3 = ['89010001#89', '89010001#89', '89010001#89', '96003010#96']
    # list4 = [{"name": "hubiao"}, {"name": "mongnet"}, {"chengji": [10, 20, 30]},
    #          {"proj": [{"projname": "项目部工程"}, {"projsize": 1024}, {"poe": [{'hu': 'adf'}]}]}]
    # list5 = [['89010001#89', '89010001#89', '89010001#89', '96003010#96'], {"name": "mongnet"},
    #          {"chengji": [10, 20, 30]}, {"proj": [{"projname": "项目部工程"}, {"projsize": 1024}, {"poe": [{'hu': 'adf'}]}]}]
    # dict4 = {"name": "hubiao", "chengji": [10, 20, 30],
    #          "proj": [{"projname": "项目部工程"}, {"projsize": 1024}, {"poe": [{'hu': 'adf'}]}]}
    # dict5 = {'busiModuleList': {'type': 'array', 'description': '流程类型id列表', 'items': {'type': 'string'}}}
    # print(generate_random_mobile())
    # print(generate_random_str())
    # print(generate_random_mail())
    # print(getStrMD5("hubiao"))
    # print(calday(3, 2015))
    # print(get_all_key(data=list4,filter_key=["name"]))
    # print(get_all_key(data=dict4))
    # print(get_all_key(data=dict5))
    # print(get_all_key(data=str2))
    # print(get_all_value(data=list4))
    # print(get_all_value(data=list5))
    # print(get_all_value(data=dict4))
    # print(get_all_value(data=dict3))
    # print(get_all_value(data=dict5))
    # name = "我是中国人"
    # ToBa = ToBase64(name)
    # print(ToBa)
    # print(FromBase64(ToBa))
    print(toFileBase64("../data/20201222101200.png"))
    print(toFileBase64("../data/config1.yaml"))
    print(getFileSize("../data/20201222101200.png"))
    # print(UnixToTime(unix=1644844153000))
    # print(gen_uuid())
    # print(gen_uuid(True))
    # print(gen_sign(getUnix(), "123456"))
    # print(gen_sign(getUnix(), True))
    # print(getUnix(current=False))
    # print(getUnix())
    # print(getUnix(day=2, scope="ams"))
    # print(getUnix(date='2017-05-09 18:31:22'))
    # print(getUnix(date='2017-05-09'))
    # print(getUnix(date='2017-05-09 18:31:22', scope="ams"))
    # print(getUnix(date='2017-05-09', scope="ams"))
    # print(getUnix(date='2017-05-09 18:31:22', day=2))
    # print(getUnix(date='2017-05-09', day=2))
    # print(getUnix(date='2017-05-09', day=2))
    # print(getUnix(date='2019-12-31'))
    # print(getUnix(date='2019-12-31 18:31:22', day=2))
    # print(UnixToTime(unix=1662432740))
    # print(UnixToTime(unix=1494325882000))
    # print(UnixToTime(unix=getUnix(date='2019-12-31 18:31:22', day=2)))
    print(file_absolute_path('../data/Quality_check_lib.xls'))
    print(type(file_absolute_path('../data/Quality_check_lib.xls')))
    print(file_absolute_path('D:/Automation\\standard_polling/data/Quality_check_lib.xls'))
    print(type(file_absolute_path('D:/Automation\\standard_polling/data/Quality_check_lib.xls')))
    print(file_is_exist('D:/Automation/standard_polling/data/Quality_check_lib.xls'))
    print(type(file_is_exist('D:/Automation/standard_polling/data/Quality_check_lib.xls')))
    print(getFileMD5('D:/Automation/standard_polling/data/Quality_check_lib.xls'))
    print(getFileName('D:/Automation/standard_polling/data/Quality_check_lib.xls'))
    source = {"ex": 1, "state": "false", "age": 38, "shool":{"name":"wgj"}}
    replaceDict = {"ex": None, "state": False, "shool": 38, "age":20, "name":"hubiao"}
    a = {"name": "hubiao", "age": 37, "age2": "37", "ex": None,  "ex2": False, "shool":{"name":"wgj"}}
    alist = [{"name":"mongnet","ex1":False,"age":37},{"name": "hubiao", "age": 37, "age2": "37", "ex": "null",  "ex2": False, "shool":{"name":"wgj"}}]
    rep = {37:38,False:True,"wgj":"mong"}
    # recursion_replace_dict_value(a,rep)
    # recursion_replace_dict_value(alist,rep)
    # print(a)
    # print(alist)
    recursion_replace_dict_key_value(source,replaceDict)
    recursion_replace_dict_key_value(alist,replaceDict)
    print(source)
    print(alist)
    matc = get_match_text("http://192.168.13.172/service/luban-file/video/view/5aa0b8944759472789e1b9183941cf32?readOnly=true&access-token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJHWkFDUHoxVlBjIiwiYXBwIjoiYnVpbGRlci1iYXNlIiwiaWF0IjoxNzI0ODI3ODI4LCJzdWIiOiJcdTgwZTFcdTVmNmEiLCJuYW1lIjoiYnVpbGRlci1iYXNlIiwiZXhwIjoxNzI0ODg3ODI4LCJhdWQiOm51bGwsImFjdCI6IkFMTCIsIm1ldGEiOnsicG5hbWUiOiJsdWJhbi1idWlsZGVyLWFwcCIsInRpZCI6OTAwMDExNTB9LCJyZXMiOm51bGwsImRhdGEiOnsidGVuYW50SWQiOjkwMDAxMTUwLCJjdXN0b21lcktleSI6bnVsbCwiY3VzdG9tZXJJZCI6bnVsbH19.YEKRhpXCrDWi82rCdImIg1kQGcaPgWvQh5zEV0WV470rFUfrm0G0FWv86xuawXQAnRWTJSXlZMUOS_GwmJVT1FekaazUUbGgdWCHzkZaPcbXsBRbzCmrlB2IL-JvPSLI1Jwcyp5nkFKZvpz1YChq8Ke0v2OKyKbvYofaZXBmsQTD0aVhoFy92VK4Y9LGd1YJ8meeHhdgn-vvvV8AxUgPrr1La0Jhm20VD3tUZRVpeNb-l8s5zSDXJqw7ncDFJ6wDXwZXD14c6jGBIr73yTFoWrc4PU5l-iYmz8pnPbCYsOmmHF__GTVrIyTgLvonW2KatYsTv9B24nWASPBdGJZ-aGB4rWlbxQ13lNg4Qi7AkHDk4to-KrVXeq_MR3-OZAS6siFXXfIQtz69SFC-TPAntdKS2QgFzM_uaMycOVjKQMRfhnJm1R1rQzcbltmpIstrcz1dQwCgQmYKlsUjmRE4MB-JBbhbDYft8OwBL0x0_cKYMO216Q7gWGofxHjQD3GlsQLT6yZiyQrXdefY_ZJhT1TK02yKyTj_Zj4JUVMxzhOWJJi31m20Id_x664eAl31JKFSfM3muyARbf91Njm_ZM-tQ1_CvQw3MIDKBCAr4c6-hmj3xherXeBJ6QlDf0Ckmj9gLVSDJvo8Kqy3aioq5AZXti1ukreW2sv0iXgO4Ek&fileIds=25a182bf50624f5694b4311e2ad445a2",textKeys=["url","previewUrl","window.fileUrl","video:"], split_str_list=[";"])
    print(matc)
    print(extract_urls(matc))

    # TextLineContains(f"http://etlview.lbuilder.cn/center-new/config.js", "serviceUrl", f"http://etlview.lbuilder.cn/api","etlview config.js 配置未修改")


