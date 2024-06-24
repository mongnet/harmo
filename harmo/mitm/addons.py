#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2019/4/3 15:12
# @Author  : hubiao

import mitmproxy.http
from mitmproxy import ctx
import time,json
from harmo import base_utils
from harmo.global_map import Global_Map
from harmo.operation import yaml_file

class Counter:
    def __init__(self,domains):
        self.domains = domains
        self.num = 0
        #self.interfaces = [['请求路径', '请求类型', '请求headers', '请求体','请求大小(b)', '响应大小', '响应类型', '请求响应时间差(s)', '请求开始时间', '请求响应结束时间']]
        self.interfaces = []
        config = yaml_file.get_yaml_data(base_utils.file_absolute_path("config.yaml"))
        Global_Map.sets(config)

    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        flow.customField = []

    def request(self, flow: mitmproxy.http.HTTPFlow):
        if self.match(flow.request.url):
            self.num = self.num + 1
            # 跳过不录制的请求方法,如：options
            if isinstance(Global_Map.get("Setting").get("filterMethod"),list) and flow.request.method.lower() in Global_Map.get("Setting").get("filterMethod"):
                return
            flow.start_time = time.time()
            flow.customField = [flow.request.url, flow.request.path, flow.request.method, dict(flow.request.headers), flow.request.get_text()]
            if flow.customField:
                self.interfaces.append(flow.customField)
            print('----------',len(self.interfaces))

    def match(self, url):
        if not self.domains:
            ctx.log.error("必须配置允许录制的域名列表")
            exit(-1)
        for domain in self.domains:
            if domain in url:
                return True
        return False

    def error(self, flow):
        flow.customField.append("Error response")

    def response(self, flow):
        if self.match(flow.send_request.url):
            # 跳过不录制的请求方法,如：options
            if isinstance(Global_Map.get("Setting").get("filterMethod"),list) and flow.send_request.method.lower() in Global_Map.get("Setting").get("filterMethod"):
                return
            flow.end_time = time.time()
            try:
                flow.customField.append(json.loads(flow.response.text))
            except:
                flow.customField.append(flow.response.text)
            try:
                flow.customField.append(flow.response.headers['Content-Type'])
            except Exception:
                flow.customField.append("")
            try:
                time_gap = flow.end_time - flow.start_time
                flow.customField.append(time_gap)
            except Exception:
                flow.customField.append("")
            self.formatoutput(flow)
            with open('script.json','w',encoding='utf-8') as f:
                f.write(json.dumps(self.clean_data(self.interfaces), ensure_ascii=False))
                f.close()

    def formatoutput(self, flow):
        if self.match(flow.send_request.url):
            ctx.log.info(f"We've seen {self.num} flows")
            try:
                flow.customField.append(flow.start_time)
            except:
                flow.customField.append("")
            try:
                flow.customField.append(flow.end_time)
            except:
                flow.customField.append("")

    def clean_data(self,interfaces):
        flowList =[]
        for interface in interfaces:
            data_json,filterInfo={},False
            if isinstance(Global_Map.get("Setting").get("filterFile"),list):
                for special in Global_Map.get("Setting").get("filterFile"):
                    if special in interface[0]:
                        filterInfo = True
                if not filterInfo and not interface[0].endswith("/"):
                    data_json['id'] = base_utils.generate_random_str(randomlength=10)
                    data_json['url'] = interface[0]
                    data_json['path'] = interface[1]
                    data_json['method'] = interface[2]
                    data_json['headers'] = interface[3]
                    try:
                        if isinstance(interface[4],dict):
                            base_utils.recursion_replace_dict_value(interface[4], Global_Map.get("Setting").get("replaceDict"))
                            data_json['body'] = interface[4]
                        elif isinstance(interface[4],list):
                            # TODO 列表替换
                            pass
                        elif 'WebKitFormBoundary' not in str(interface[4]):
                            if interface[4] !='' :
                                data_json['body'] = eval(str(interface[4]).replace('null','None').replace('true','True').replace('false','False'))
                            else:
                                data_json['body'] = None
                        else:
                            body = str(interface[4])
                            bodylist = body.split('\r\n')
                            data_json['body']={}
                            for each in bodylist:
                                if 'name=' in each:
                                    if 'file' not in str(each) and 'attachment' not in str(each):
                                        data_json['body'][each.split('\"')[1]] = bodylist[int(int(bodylist.index(each))+2)]
                                    else:
                                        data_json['body']['doc'] = each.split('\"')[1]
                    except:
                        data_json['body'] = None
                    try:
                        if isinstance(interface[5],dict):
                            base_utils.recursion_replace_dict_value(interface[5], Global_Map.get("Setting").get("replaceDict"))
                            data_json['resp'] = interface[5]
                            ctx.log.error(f"resp:{interface[5]}")
                        elif isinstance(interface[5],list):
                            # TODO 列表替换
                            pass
                    except:
                        data_json['resp'] = None
            flowList.append(data_json)
        return flowList

addons = [
    Counter(
        # 允许录制的域名列表
        [
            "http://127.0.0.1:5000",
            "lbuilder.cn"
        ],
    )
]

