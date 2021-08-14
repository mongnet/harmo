#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @TIME    : 2018/7/31 17:18
# @Author  : hubiao
# @File    : base_requests.py
import copy
import json
import logging
from mimetypes import MimeTypes

import requests

from luban_common import base_utils


class Send:
    """
    发送请求类
    """
    def __init__(self,host,envConf,global_cache=None,header=None):
        """
        请求数据初始化
        :param host：请求的地址前缀
        :param envConf：环境配置信息
        :param global_cache：缓存信息
        :param header：请求头信息
        """
        self.host = host
        self.cache = global_cache
        self.session = requests.session()
        if "headers" in envConf:
            self.header = envConf["headers"]["json_header"] if header is None else header
            self.pdsUrl = envConf["pds"]
        else:
            # wgj新增，不动原有逻辑，不传入pds
            self.header = envConf

    def request(self, method, address, payload=None, header=None, flush_header=False, files=None, params=None, cookies_kwargs=None,timeout=60,**kwargs):
        """
        封装request方法，要求传三个参数
        :param method：请求的方式post,get,delete,put等
        :param address：请求的地址
        :param payload：请求的body数据，可以不传，默认为空
        :param header：header信息
        :param flush_header: 刷新header，比如token就要通过flush_header
        :param files：上传文件时的文件信息
        :param params: URL传参，接收一个字典数据
        :param cookies_kwargs: cookie参数，接收一个字典数据
        :return: 对响应信息进行重组，响应信息中加入status_code和responsetime
        """
        # 如果address不是http开头，组装请求地址
        self.Url = address if address.startswith("http") else "".join([self.host,address])
        request_header = copy.deepcopy(json.loads(self.header) if not isinstance(self.header, dict) else self.header)
        # 添加header信息，有些接口请求时添加请求头,flush_header用来指定是否更新基线header
        if header is not None:
            header = json.loads(header) if not isinstance(header, dict) else header
            request_header.update(header)
            if flush_header:
                self.header = json.loads(self.header) if not isinstance(self.header, dict) else self.header
                self.header.update(header)
        # 添加cookies信息，有些接口请求时要在cookies上添加信息
        if cookies_kwargs is not None:
            if isinstance(cookies_kwargs,dict):
                for key, value in cookies_kwargs.items():
                    self.session.cookies.set(key,value)
            else:
                raise TypeError("cookies_kwargs 必须是dict类型")
        # 默认上传文件时不指定Content-Type,files会自动添加Content-Type,人为指定容易出错
        if files is not None:
            # 指定header时跳过删除类型
            if header is None:
                del request_header["Content-Type"]
            # 上传文件时在框架中直接判断文件是否存在，调用时可只传文件路径即可
            if isinstance(files,dict) and "file" in files.keys():
                pass
            else:
                base_utils.file_is_exist(files)
                filename = base_utils.getFileName(files)
                fileType = MimeTypes().guess_type(files)[0]
                if fileType is None:
                    files = {"file": (filename,open(files, "rb"))}
                else:
                    files = {"file": (filename, open(files, "rb"),fileType)}
        # 判断payload不为str时，dumps成str类型
        if isinstance(payload,list) or (not isinstance(payload,str) and payload):
            payload = json.dumps(payload)
        res = {}
        try:
            # 发送POST请求
            self.Response = self.session.request(method=method, url=self.Url, data=payload, headers=request_header, hooks=dict(response=self.hooks), params=params, timeout=timeout, files=files)
            # 解决跨域302跳转后响应成cas登录页面的处理，当出现cas登录界面时自动重试相关接口
            if self.Response.status_code == 200 and "/login?service=" in self.Response.url:
                self.Response = self.session.request(method=method, url=self.Url, data=payload, headers=request_header, params=params, timeout=timeout, files=files)

            try:
                # 获取请求和响应数据
                logging.info("开始分割线start: ".center(60, "#"))
                logging.info("请求方法: " + method)
                logging.info(list(kwargs.keys())[0]+": "+kwargs[list(kwargs.keys())[0]]) if kwargs!={} else None
                logging.info("请求的Url: " + self.Url)
                logging.info("持续时间: " + str(self.Response.elapsed.total_seconds()))
                logging.info("请求头: " + str(self.Response.request.headers))
                logging.info("请求数据: " + str(payload).encode("utf-8").decode("unicode_escape"))
                logging.info("响应状态: " + str(self.Response.status_code))
                logging.info("响应内容: "+ self.Response.text if "text/html" not in str(self.Response.headers.get("Content-Type")) else "响应内容: 内容为html，隐藏")
                logging.info("结束分割线end: ".center(60, "#"))
                res["status_code"] = self.Response.status_code
                res["response_time"] = self.Response.elapsed.microseconds/1000
                res["response_header"] = self.Response.headers
                res["request_header"] = self.Response.request.headers
                res["request_url"] = self.Url
                res["request_method"] = method
                res["request_params"] = params
                res["request_payload"] = str(payload).encode("utf-8").decode("unicode_escape")
            except BaseException as e:
                logging.error("获取请求和响应信息出现异常：" + str(e))
            # 当响应体为json类型，且响应信息不为空时
            try:
                self.Response.json()
                #响应信息不为空
                if self.Response.text:
                    Response = json.loads(self.Response.text)
                    # 判断如果响应信息为dict、list时，合并逻辑
                    if isinstance(Response,(dict,list)):
                        #合并添加的http状态和返回的响应内容
                        res = {**res, **base_utils.ResponseData(Response)}
                    else:
                        # 非dict、list响应情况，直接把响应信息返回
                        res["Response_text"] = self.Response.text
                        res["Response_content"] = self.Response.content
            except:
                #非json响应信息时的处理，直接把响应信息返回
                res["Response_text"] = self.Response.text
                res["Response_content"] = self.Response.content
        except requests.exceptions.RequestException as e:
            logging.error("RequestException异常开始分割线start: ".center(60, "#"))
            logging.error("请求的Url: " + self.Url)
            logging.error("请求数据: " + str(payload).encode("utf-8").decode("unicode_escape"))
            logging.error("发送请求出现异常: " + str(e))
            logging.error("RequestException异常结束分割线end: ".center(60, "#"))
            res["status_code"] = 10004
            res["request_header"] = request_header
            res["request_url"] = self.Url
            res["request_method"] = method
            res["request_params"] = params
            res["request_payload"] = str(payload).encode("utf-8").decode("unicode_escape")
            res["Response_text"] = "发送请求出现异常，异常信息为: " + str(e)
        return res

    def hooks(self,r,*args, **kwargs):
        """
        为解决cas 302跳转时，requests无法跨域传递cookie实现的钩子方法，人为指定cookie并手动请求302跳转
        :param r: 原始请求的响应信息
        :param args:
        :param kwargs:
        """
        try:
            # 保存cas和CASTGC Cookie，在cas地址进行302跳转时使用
            if r.status_code == 200 and "Cookie" in r.request.headers.keys() and "CASTGC"in r.request.headers.get("Cookie") and self.pdsUrl in r.request.url:
                # 保存cas和CASTGC Cookie，在cas地址进行302跳转时使用
                self.cache.set("CasCookie", r.request.headers.get("Cookie"))
            # 如果响应码是302，且location是cas地址的跳转时，要加上cas的cookie并跳转这个location，如果取到的CasCookie为False时不跳转
            elif r.status_code == 302 and "Location" in r.headers.keys() and self.pdsUrl in r.headers.get("Location") and self.cache.get("CasCookie",False):
                header = json.loads(self.header)
                header.update({"cookie":self.cache.get("CasCookie",False)})
                self.session.request(method=r.request.method, url=r.headers.get("Location"), headers=header,
                                     timeout=60)
        except BaseException as e:
            logging.error("302异常开始分割线start: ".center(60, "#"))
            logging.error("302跳转Url: " + r.request.url)
            logging.error("302跳转出现异常: " + str(e))
            logging.error("302异常结束分割线end: ".center(60, "#"))

if __name__ == "__main__":
    pass