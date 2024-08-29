#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2018/7/31 17:18
# @Author  : hubiao
# @File    : http_requests.py
import copy
import json
import logging
import re

import requests
import urllib3
from mimetypes import MimeTypes
from typing import Optional
from harmo import base_utils, exceptions
from harmo.global_map import Global_Map

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HttpRequests(requests.Session):
    """
    发送请求类
    """
    def __init__(self,base_url: str, header: Optional[dict]=None):
        """
        请求数据初始化
        :param base_url：请求的地址前缀
        :param header：请求头信息
        """
        super(HttpRequests, self).__init__()
        # 基础url
        if re.compile(r"(http)(s?)(://)").match(base_url):
            self.base_url = base_url
        else:
            raise exceptions.ParserError("base url do you mean http:// or https://!")
        self.session = requests.session()
        if header:
            self.header = json.loads(header) if not isinstance(header, dict) else header
        else:
            self.header = {
                "Accept": "application/json,text/plain",
                "User-Agent": "Mozilla/5.0(Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400",
                "Content-Type": "application/json;charset=utf-8",
                "Accept-Encoding":"gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8"
            }
        self.casUrl = Global_Map.get("cas")

    def send_request(self, method: str, url: str, payload=None, header: Optional[dict]=None, flush_header=False, files: Optional[dict]=None, params: Optional[dict]=None, cookies_kwargs: Optional[dict]=None, timeout=60, **kwargs):
        """
        封装request方法
        :param method：请求的方式post,get,delete,put等
        :param url：请求的url地址
        :param payload：请求的body数据，可以不传，默认为空
        :param header：header信息
        :param flush_header: 刷新header，默认临时刷新，只对当前请求有效，当传True时会刷新整个session，后续请求都会用新header
        :param files：上传文件时的文件信息，files={'file': 'data/签章文件.pdf'}
        :param params: URL传参，接收一个字典数据
        :param cookies_kwargs: cookie参数，接收一个字典数据
        :param timeout: 超时时间，默认60s
        :return: 对响应信息进行重组，响应信息中加入status_code和responsetime
        """
        # 拼接url，默认使用初始化的self.base_url，但如果指定了base_url，就使用base_url
        base_url = kwargs.get("base_url", None)
        if re.compile(r"(http)(s?)(://)").match(url):
            self.Url = url
        elif base_url:
            if re.compile(r"(http)(s?)(://)").match(base_url):
                self.Url = "".join([base_url,url])
            else:
                raise exceptions.ParserError("base url do you mean http:// or https://!")
        else:
            self.Url = "".join([self.base_url,url])
        request_header = copy.deepcopy(self.header)
        # 添加header信息，有些接口请求时添加请求头,flush_header用来指定是否更新基线header
        if header:
            header = json.loads(header) if not isinstance(header, dict) else header
            request_header.update(header)
            if flush_header:
                self.header.update(header)
        # 添加cookies信息，有些接口请求时要在cookies上添加信息
        if cookies_kwargs:
            if isinstance(cookies_kwargs,dict):
                for key, value in cookies_kwargs.items():
                    self.session.cookies.set(key,value)
            else:
                raise TypeError("cookies_kwargs 必须是dict类型")
        # 默认上传文件时不指定Content-Type,files会自动添加Content-Type,人为指定容易出错
        if files:
            # 上传文件时在框架中直接判断文件是否存在，调用时可只传文件路径即可
            if isinstance(files, dict) and "file" in files.keys():
                filepath = base_utils.file_absolute_path(files.get("file"))
                if isinstance(header, dict) and 'application/octet-stream' in header.values():
                    payload = open(filepath, 'rb')
                    files = None
                else:
                    files = {'file': (base_utils.getFileName(filepath), open(filepath, 'rb'))}
                # 上传文件时，如果没有指定header，则删除Content-Type
                if header is None:
                    del request_header["Content-Type"]
            else:
                raise TypeError("files参数格式错误,files必须为dict类型，且必须包含file")
        # 判断payload不为str时，dumps成str类型，如果已经是str格式，尝试反序列化后再序列化
        if isinstance(payload,list) or (not isinstance(payload,str) and payload):
            payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        elif isinstance(payload, str):
            try:
                payload = json.loads(payload)
                payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            except Exception as e:
                payload = payload
        res = {}
        try:
            # 发送POST请求
            self.Response = self.session.request(method=method, url=self.Url, data=payload, headers=request_header, hooks=dict(response=self.hooks), params=params, timeout=timeout, files=files, verify=False)
            # 解决跨域302跳转后响应成cas登录页面的处理，当出现cas登录界面时自动重试相关接口
            if self.Response.status_code == 200 and "/login?service=" in self.Response.url:
                self.Response = self.session.request(method=method, url=self.Url, data=payload, headers=request_header, params=params, timeout=timeout, files=files, verify=False)

            try:
                # 获取请求和响应数据
                logging.info("开始分割线start: ".center(60, "#"))
                logging.info("请求方法: " + str(self.Response.request.method))
                logging.info(list(kwargs.keys())[0]+": "+str(kwargs[list(kwargs.keys())[0]])) if kwargs!={} else None
                logging.info("请求的Url: " + self.Response.url)
                logging.info("持续时间: " + str(self.Response.elapsed.total_seconds()))
                logging.info("请求头: " + str(self.Response.request.headers))
                logging.info("请求数据: " + str(payload.decode('utf-8') if payload else payload))
                logging.info("响应状态: " + str(self.Response.status_code))
                logging.info("响应内容: "+ self.Response.text if "text/html" not in str(self.Response.headers.get("Content-Type")) else "响应内容: 内容为html，隐藏")
                logging.info("结束分割线end: ".center(60, "#"))
                res["status_code"] = self.Response.status_code
                res["response_time"] = self.Response.elapsed.microseconds/1000
                res["response_header"] = json.loads(json.dumps(dict(self.Response.headers)))
                res["request_header"] = json.loads(json.dumps(dict(self.Response.request.headers)))
                res["request_url"] = self.Response.url
                res["request_method"] = str(self.Response.request.method)
                res["request_params"] = params
                res["request_payload"] = payload.decode('utf-8') if payload else payload
                res["response_obj"] = self.Response
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
            logging.error("请求数据: " + str(payload.decode('utf-8') if payload else payload))
            logging.error("发送请求出现异常: " + str(e))
            logging.error("RequestException异常结束分割线end: ".center(60, "#"))
            res["status_code"] = None
            res["request_header"] = request_header
            res["request_url"] = self.Url
            res["request_method"] = method
            res["request_params"] = params
            res["request_payload"] = payload.decode('utf-8') if payload else payload
            res["Response_text"] = "发送请求出现异常，异常信息为: " + str(e)
        Global_Map.sets({"temp_user_properties": {"url":res.get("request_url",None),"status_code":res.get("status_code",None),"source_response":res.get("source_response",None)}})
        return res

    def hooks(self,r,*args, **kwargs):
        """
        为解决cas 302跳转时，requests无法跨域传递cookie实现的钩子方法，指定cookie并自动请求302跳转
        :param r: 原始请求的响应信息
        :param args:
        :param kwargs:
        """
        try:
            # 保存cas和CASTGC Cookie，在cas地址进行302跳转时使用
            if r.status_code == 200 and "Cookie" in r.send_request.headers.keys() and "CASTGC"in r.send_request.headers.get("Cookie") and self.casUrl in r.send_request.url:
                # 保存cas和CASTGC Cookie，在cas地址进行302跳转时使用
                Global_Map.set("CasCookie", r.send_request.headers.get("Cookie"))
            # 如果响应码是302，且location是cas地址的跳转时，要加上cas的cookie并跳转这个location，如果取到的CasCookie为False时不跳转
            elif r.status_code == 302 and "Location" in r.headers.keys() and self.casUrl in r.headers.get("Location") and Global_Map.get("CasCookie"):
                header = self.header
                header.update({"cookie":Global_Map.get("CasCookie")})
                self.session.request(method=r.send_request.method, url=r.headers.get("Location"), headers=header,
                                     timeout=60, verify=False)
        except BaseException as e:
            logging.error("302异常开始分割线start: ".center(60, "#"))
            logging.error("302跳转Url: " + r.send_request.url)
            logging.error("302跳转出现异常: " + str(e))
            logging.error("302异常结束分割线end: ".center(60, "#"))

if __name__ == "__main__":
    pass