#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022-12-11 17:08
# @Author : hubiao
# @Email : xxx@gmail.com
# @File : mitm_record.py

# mitmproxy录制流量自动生成用例

import os
import time
import mitmproxy.http
from luban_common import base_utils
from mitmproxy import ctx

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tests_dir = os.path.join(project_dir, "tests")
# tests/mitm
mitm_dir = os.path.join(tests_dir, "")
if not os.path.exists(mitm_dir):
    os.mkdir(mitm_dir)
# 当前时间作为文件名
filename = f'test_{time.strftime("%Y%m%d_%H%M%S", time.localtime())}.py'
case_file = os.path.join(mitm_dir, filename)
# 生成用例文件
template = """import allure
from luban_common import base_requests
@allure.title("")
def test(env_vars):
"""
if not os.path.exists(case_file):
    with open(case_file, "w", encoding="utf8") as fw:
        fw.write(template)


class Record:
    def __init__(self, domains):
        self.domains = domains

    def response(self, flow: mitmproxy.http.HTTPFlow):
        if self.match(flow.request.url):
            # method
            method = flow.request.method.lower()
            # options 请求直接跳过不录制
            if method in ["options"]:
                return
            # url
            url = flow.request.url
            # status_code
            status_code = flow.response.status_code
            # headers
            headers = dict(flow.request.headers)
            # body
            try:
                body = flow.request.json()
                base_utils.recursion_replace_dict_value(body, {"false":False})
            except:
                body = flow.request.text
            ctx.log.error(body)
            with open(case_file, "a", encoding="utf8") as fa:
                fa.write(self.step(method, url, headers, body))

    def match(self, url):
        if not self.domains:
            ctx.log.error("必须配置允许录制的域名列表")
            exit(-1)
        for domain in self.domains:
            if domain in url:
                return True
        return False

    def step(self, method, url, headers, body):
        '''
        生成步骤
        :param method:
        :param url:
        :param headers:
        :param body:
        :return:
        '''
        body_grammar = None
        if method == "get":
            if body:
                body_grammar = f"params={body}"
        else:
            if body:
                body_grammar = f"data={body}"
        return f"""
            # 描述
            # 数据
            # 请求
            req = base_requests.Send(url)
            resp = req.request(
                method = "{method}",
                url = "{url}",
                headers = "{headers}",
                {body_grammar})
            # 提取
            # 断言
            assert resp.status_code < status_code
        """


# ==================================配置开始==================================
addons = [
    Record(
        # 允许录制的域名列表
        [
            "http://127.0.0.1:5000",
            "lbuilder.cn"
        ],
    )
]
# ==================================配置结束==================================

"""
==================================命令说明开始==================================
# 正向代理（需要手动打开代理）
mitmdump -s mitm_record.py
# 反向代理
mitmdump -s mitm_record.py --mode reverse:http://127.0.0.1:5000 --listen-host 127.0.0.1 --listen-port 8000
==================================命令说明结束==================================
"""
if __name__ == '__main__':
    pass