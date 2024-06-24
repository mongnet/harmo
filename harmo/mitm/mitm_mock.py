#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023-4-21 23:48
# @Author : hubiao
# @Email : xxx@gmail.com
# @File : mitm_mock.py

from mitmproxy import http,ctx

class Record:
    def __init__(self, domains):
        self.domains = domains

    def request(self, flow: http.HTTPFlow):
        if self.match(flow.request.url):
            print("拦截前的访问地址：",flow.request.url)
            if flow.request.pretty_host == "127.0.0.1":
                flow.request.host = "101.132.100.33"
                flow.request.port = 5000
                print("拦截后访问地址：",flow.request.url)

    def match(self, url):
        if not self.domains:
            ctx.log.error("必须配置允许录制的域名列表")
            exit(-1)
        for domain in self.domains:
            if domain in url:
                return True
        return False

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