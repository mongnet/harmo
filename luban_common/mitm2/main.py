#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2019/4/3 15:12
# @Author  : hubiao

from luban_common.global_map import Global_Map
from luban_common.operation import yaml_file
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from luban_common import base_utils
import mitmproxy.http
from mitmproxy import ctx
import json
import asyncio
import time
import os
import signal

class Counter(object):
    def __init__(self,domains):
        self.domains = domains
        self.interfaces = []
        ctx.log.error("start:hubiao")
        config = yaml_file.get_yaml_data(base_utils.file_absolute_path("config.yaml"))
        Global_Map.sets(config)

    def match(self, url):
        ctx.log.error("match")
        if not self.domains:
            ctx.log.error("必须配置允许录制的域名列表")
            exit(-1)
        for domain in self.domains:
            if domain in url:
                return True
        return False

    def request(self, flow: mitmproxy.http.HTTPFlow):
        ctx.log.error("hubiao")
        if self.match(flow.request.url):
            # 跳过不录制的请求方法,如：options
            if isinstance(Global_Map.get("Setting").get("filterMethod"),list) and flow.request.method.lower() in Global_Map.get("Setting").get("filterMethod"):
                return
            flow.start_time = time.time()
            flow.customField = [flow.request.url, flow.request.path, flow.request.method, dict(flow.request.headers), flow.request.get_text()]
            if flow.customField:
                self.interfaces.append(flow.customField)
            print('----------',len(self.interfaces))

    def response(self, flow):
        ctx.log.error("resp")
        if self.match(flow.send_request.url):
            # 跳过不录制的请求方法,如：options
            if isinstance(Global_Map.get("Setting").get("filterMethod"),list) and flow.send_request.method.lower() in Global_Map.get("Setting").get("filterMethod"):
                return
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
            with open('script.json','w',encoding='utf-8') as f:
                f.write(json.dumps(self.clean_data(self.interfaces), ensure_ascii=False))
                f.close()

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


addons = [Counter([
    "http://127.0.0.1:5000",
    "lbuilder.cn"
])]
opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
master = DumpMaster(options=opts,with_dumper=True,with_termlog=True)
master.addons.add(addons)


loop = asyncio.get_event_loop()
loop.create_task(asyncio.run(addons))
# 键盘中 Ctrl-C 组合键信号
loop.add_signal_handler(signal.SIGINT, getattr(master, "prompt_for_exit", master.shutdown))
# 命令行数据 kill pid 时的信号
loop.add_signal_handler(signal.SIGTERM, master.shutdown)
# nohup 守护进程发出的关闭信号
loop.add_signal_handler(signal.SIGHUP, master.shutdown)

master.run()