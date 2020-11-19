#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by hubiao on 2017/5/9
from __future__ import print_function

import base64
import calendar
import hashlib
import os
import random
import re
import requests
import subprocess
import time
import yaml
from datetime import datetime
from datetime import timedelta

import jsonpath
from pathlib2 import Path


def getFileMD5(file_Path):
    '''
    传入文件路径，返回文件MD5
    :param file_Path: 文件路径，相对于项目根目录，如 data/Doc/Lubango20191205.docx
    :return: MD5值
    '''
    file = file_is_exist(file_Path)
    try:
        fileObjct = open(file, 'rb')
        m = hashlib.md5()
        while True:
            d = fileObjct.read(4096) #每次读取4KB的数据
            if not d: break #如果读出来的数据为空时跳出循环
            m.update(d)
        fileObjct.close()
        return m.hexdigest()
    except Exception as e:
        return None

def getFileSize(file_Path):
    '''
    传入文件路径，返回文件大小
    :param file_Path: 文件路径，相对于项目根目录，如 data/Doc/Lubango20191205.docx
    :return: 文件大小
    '''
    file = file_is_exist(file_Path)
    filesize = os.path.getsize(file)
    return filesize

def getFileName(file_Path):
    '''
    传入文件路径，返回文件名称
    :param file_Path: 文件路径，相对于项目根目录，如 data/Doc/Lubango20191205.docx
    :return: 文件名
    '''
    file = file_is_exist(file_Path)
    fileName = os.path.basename(file)
    return fileName

def file_is_exist(file_path):
    '''
    判断文件是否存在
    :param file_path:
    :return:
    '''
    if not Path(file_path).exists():
        raise FileNotFoundError("请确认路径或文件是否正确！")
    return file_path

def getStrMD5(String):
    '''
    传入一个字符串，返回字符串MD5值
    :param String: 字符串
    :return: MD5值
    '''
    if not isinstance(String,str):
        raise TypeError("只支持字符串类型")
    m = hashlib.md5()
    m.update(String.encode('utf-8'))
    return m.hexdigest()

def getStrSha1(String):
    """
    sha1 算法加密
    :param msg: 需加密的字符串
    :return: 加密后的字符
    """
    if not isinstance(String,str):
        raise TypeError("只支持字符串类型")
    sh = hashlib.sha1()
    sh.update(String.encode('utf-8'))
    return sh.hexdigest()

def ToBase64(String):
    '''
    传入一个字符串，返回字符串的Base64
    :param String: 字符串
    :return: Base64
    '''
    if not isinstance(String,str):
        raise TypeError("只支持字符串类型")
    base64Str = base64.b64encode(String.encode("utf-8"))
    return str(base64Str,'utf-8')

def FromBase64(String):
    '''
    传入一个Base64，返回字符串
    :param String: 字符串
    :return: 返回字符串
    '''
    if not isinstance(String,str):
        raise TypeError("只支持字符串类型")
    missing_padding = 4 - len(String) % 4
    if missing_padding:
        String += '=' * missing_padding
    return str(base64.b64decode(String),'utf-8')

def getUnix(date=None):
    '''
    通过传入的时间获取时间戳，默认获取当前时间戳
    :param date:传入的时间，格式为：'2017-05-09 18:31:22' 
    :return: 返回时间戳
    '''
    if date is None:
        ST = datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"%Y-%m-%d %H:%M:%S")
    else:
        ST = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    unixST = int(time.mktime(ST.timetuple())) * 1000
    return str(unixST)

def UnixToTime(unix):
    '''
    把时间戳转换成时间
    :param unix: 时间戳
    :return: 返回时间
    '''
    time_local = time.localtime(int(unix)/1000)
    dt = time.strptime(time.strftime("%Y-%m-%d %H:%M:%S",time_local),"%Y-%m-%d %H:%M:%S")
    return dt

def getRecentMonthOfDay():
    '''
    获取近一个月的开始时间,比如今天是2016-12-15 12:25:00，那么返回的时间为2016-11-15 00:00:00
    :return: 返回最近一个月的开始时间
    '''
    d = datetime.strptime(time.strftime('%Y-%m-%d',time.localtime(time.time())),"%Y-%m-%d")
    year = d.year
    month = d.month

    if month == 1 :
        month = 12
        year -= 1
    else :
        month -= 1
    days = calendar.monthrange(year, month)[1]
    #上月同一天00:00到当前这一刻，认定为最近一月，如果要为上一天数据days减1即可
    day = d- timedelta(days=days)
    unixtime = int(time.mktime(day.timetuple()))*1000
    return unixtime,day

def calday(month, year):
    '''
    根据指定的年月，返回当月天数
    :param month: 月份
    :param year: 年份
    :return: 返回指定年月当月天数
    '''
    if not isinstance(month,int) and not isinstance(year,int):
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
    :return: 返回执行结束
    '''
    output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    o = output.decode("utf-8")
    return o

def generate_random_str(randomlength=8):
    '''
    生成随机字符串
    :param randomlength: 默认8个字符
    :return: 返回随机字符串
    '''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    return "".join(random.choice(base_str) for i in range(randomlength))

def generate_random_mail():
    '''
    生成随机邮件地址
    :return: 返回随机邮件地址
    '''
    postfix = ["163.com", "126.com", "qq.com", "yahoo.com.cn"]
    return generate_random_str() + "@" + random.choice(postfix)

def generate_random_mobile():
    '''
    生成随机手机号
    :return:
    '''
    prefix = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
                 "141", "145", "146", "147", "150", "151", "152", "153", "155", "156", "157", "158", "159","166",
                 "170", "172", "173", "174", "176", "177", "178", "180", "181", "182", "183", "184", "185", "186", "187", "188", "189",
                 "198", "199"]
    return random.choice(prefix)+"".join(random.choice("0123456789") for i in range(8))

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
        templist,result, key = [],{}, []
        try:
            for i in dict_generator(indict):templist.append(i)
        except:
            pass
            # for i in dict_generator(eval(json.dumps(dict(xmltodict.parse(data))))):templist.append(i)
        for value in templist:key.append(value[0])
        for keys in list(set(key)):
            result[keys]=[]
            for values in templist:
                if keys == values[0]:result[keys].append(values[1])
        result["source_response"] = indict
        return result
    except BaseException as e:
        print(str(e))

def Search_tag_text(url,tag,text):
    '''
    请求网页并搜索指定的html标签内是否有指定文本
    :param url: 指定要检查的连接地址
    :param label: 指定要检查的html或xml标签，不要尖括号，如:h2
    :param text: 指定要检查是否存在的文本
    :return:
    '''
    try:
        # 请求服务器
        resp = requests.get(url)
    except requests.exceptions.RequestException as e:
        assert False,f'请求连接地址出错，错误信息为:{e}'
    # 查询指定标签
    obj = re.search(f'<{tag}>(.*)</{tag}>',resp.text)
    # 判断是否找到指定标签
    if not obj:
        assert False,f'not found {tag}'
    # 判断标签中的值是否为指定的文本
    if not obj.group(1)==text:
        assert False,f'not found {text}'

def time_difference(start_time,end_time):
    '''
    获取时间差
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: 返回时间差(秒)
    '''
    if isinstance(start_time,datetime):
        return (end_time - start_time).seconds
    else:
        raise TypeError("只支持 datetime 类型")

def jpath(data,check_key,check_value=None,sub_key=None):
    '''
    jsonpath封装,例：jsonpath.jsonpath(data,$..[?(@.functionKey=='D-2')]..openStatus)
    :param data: 需要获取的数据,类型必须是dict,否侧返回False
    :param check_key: 检查key,例子中的functionKey
    :param check_value: 检查value,辅助定位,例子中的'D-2'
    :param sub_key: 检查子key,辅助定位,例子中的openStatus,当指定sub_key时,只返回sub_key对应的values,其它数据不返回
    :return: 返回一个list,当匹配不到数据时,返回False
    '''
    # if not isinstance(data,dict):
    #     return False
    if check_value is not None:
        if isinstance(check_value,int):
            expr = f"$..[?(@.{check_key}=={check_value})]" if sub_key is None else f"$..[?(@.{check_key}=={check_value})]..{sub_key}"
        elif isinstance(check_value,str):
            expr = f'$..[?(@.{check_key}=="{check_value}")]' if sub_key is None else f'$..[?(@.{check_key}=="{check_value}")]..{sub_key}'
        else:
            return False
    else:
        expr = f"$..[?(@.{check_key})]" if sub_key is None else f"$..[?(@.{check_key})]..{sub_key}"
    return jsonpath.jsonpath(data,expr)

if __name__ == "__main__":
    print(generate_random_mobile())
    print(generate_random_str())
    print(generate_random_mail())
    print(getStrMD5("hubiao"))
    print(calday(3,2015))
    time1 = datetime.now()
    time.sleep(2)
    time2 = datetime.now()
    print(time_difference(time1, time2))


