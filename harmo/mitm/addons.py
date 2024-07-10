#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2019/4/3 15:12
# @Author  : hubiao

from mitmproxy import http
from mitmproxy import ctx
import time,json
from harmo import base_utils
from harmo.global_map import Global_Map
from harmo.operation import yaml_file

Global_Map.sets(yaml_file.get_yaml_data(base_utils.file_absolute_path("config.yaml")))

class Counter:
    def __init__(self,domains):
        self.domains = domains
        self.interfaces = []

    def request(self, flow: http.HTTPFlow):

        # 记录请求信息
        if self.match(flow.request.url):
            # 跳过不录制的请求方法,如：options
            if isinstance(Global_Map.get("Setting").get("filterMethod"),list) and flow.request.method.lower() in Global_Map.get("Setting").get("filterMethod"):
                return
            flow.customField = {}
            flow.start_time = time.time()
            flow.customField.update({"url": flow.request.url})
            flow.customField.update({"path": flow.request.path})
            flow.customField.update({"method": flow.request.method})
            flow.customField.update({"headers": dict(flow.request.headers)})
            flow.customField.update({"body": flow.request.get_text()})

    def match(self, url):
        if not self.domains:
            ctx.log.error("必须配置允许录制的域名列表")
            exit(-1)
        for domain in self.domains:
            if domain in url:
                return True
        return False

    def response(self, flow):
        if self.match(flow.request.url):
            # 跳过不录制的请求方法,如：options
            if isinstance(Global_Map.get("Setting").get("filterMethod"),list) and flow.request.method.lower() in Global_Map.get("Setting").get("filterMethod"):
                return
            flow.end_time = time.time()
            try:
                flow.customField.update({"resp": json.loads(flow.response.text)})
            except:
                flow.customField.update({"resp": flow.response.text})
            try:
                flow.customField.update({"time_gap": flow.end_time - flow.start_time})
            except Exception:
                flow.customField.update({"time_gap": ""})
            clean_result = self.clean_data(flow.customField)
            if clean_result:
                self.interfaces.append(clean_result)
                ctx.log.info(f"发现第： {len(self.interfaces)} 个接口")
                with open('script.json','w',encoding='utf-8') as f:
                    f.write(json.dumps(self.interfaces, ensure_ascii=False))

    def clean_data(self,interface):
        if isinstance(interface,dict):
            data_json,filterInfo={},False
            if isinstance(Global_Map.get("Setting").get("filterFile"),list):
                for special in Global_Map.get("Setting").get("filterFile"):
                    if special in interface.get("url"):
                        filterInfo = True
                if not filterInfo and not interface.get("url").endswith("/"):
                    data_json['id'] = base_utils.generate_random_str(randomlength=10)
                    data_json['url'] = interface.get("url")
                    data_json['path'] = interface.get("path")
                    data_json['method'] = interface.get("method")
                    data_json['headers'] = interface.get("headers")
                    try:
                        if isinstance(interface.get("body"),(dict,list)):
                            base_utils.recursion_replace_dict_value(interface.get("body"), Global_Map.get("Setting").get("replaceDict"))
                            data_json['body'] = interface.get("body")
                        elif 'WebKitFormBoundary' not in str(interface.get("body")):
                            if interface.get("body") !='' :
                                data_json['body'] = eval(str(interface.get("body")).replace('null','None').replace('true','True').replace('false','False'))
                                # data_json['body'] = interface.get("body")
                            else:
                                data_json['body'] = None
                        else:
                            body = str(interface.get("body"))
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
                        base_utils.recursion_replace_dict_value(interface.get("resp"), Global_Map.get("Setting").get("replaceDict"))
                        data_json['resp'] = interface.get("resp")
                    except:
                        data_json['resp'] = None
            if data_json:
                return data_json
        return

def getAllowRecording() -> list:
    """
    获取允许录制的域名列表
    :return:
    """
    AllowRecording = Global_Map.get("Setting").get("AllowRecording")
    if isinstance(AllowRecording, list) and AllowRecording:
        return AllowRecording
    raise TypeError("必须配置允许录制的域名列表")

addons = [
    Counter(
        # 允许录制的域名列表
        getAllowRecording()
    )
]