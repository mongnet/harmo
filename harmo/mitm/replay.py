#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com
import copy
from datetime import datetime
from typing import Optional

import jsonpath
import requests

from harmo.mitm.NoiseReduction import NoiseReduction
from harmo.mitm.report import ReportUtil
from harmo.msg.robot import WeiXin
from harmo.operation import yaml_file
from harmo import http_requests, extract, base_utils
from harmo.global_map import Global_Map
from urllib.parse import urlparse

def assert_json(actual, expect):
    '''

    :param actual:
    :param expect:
    :return:
    '''
    actual = base_utils.ResponseData(actual)
    expect = base_utils.ResponseData(expect)
    errorList = []
    del actual['source_response']
    del expect['source_response']
    base_utils.recursion_replace_dict_value(actual, {'null': None, 'false': False, 'true': True})
    base_utils.recursion_replace_dict_value(expect, {'null': None, 'false': False, 'true': True})
    for key in expect.keys():
        temp_dict = {}
        if '{' not in str(expect[key]):
            if len(expect[key]) != 0:
                if isinstance(expect[key][0], (str, float, int)):
                    try:
                        actual_val = actual[key]
                    except:
                        actual_val = actual.get(key, None)
                    try:
                        expect_val = expect[key]
                    except:
                        expect_val = expect.get(key, None)
                    try:
                        if actual_val == expect_val:
                            if list(set(actual_val).difference(set(expect_val))) != []:
                                temp_dict['key'] = key
                                temp_dict['expect'] = expect_val
                                temp_dict['actual'] = actual_val
                        else:
                            temp_dict['key'] = key
                            temp_dict['expect'] = expect_val
                            temp_dict['actual'] = actual_val
                    except:
                        temp_dict['key'] = key
                        temp_dict['expect'] = expect_val
                        temp_dict['actual'] = actual_val
        if temp_dict != {}:
            errorList.append(temp_dict)
    return errorList

class Replay:
    """
    流量回放
    """
    def __init__(self):
        Global_Map.sets(yaml_file.get_yaml_data_all(base_utils.file_absolute_path("conifg")))
        self.noiseReduction = NoiseReduction()
        self.data = {}
        self.diff = None
        self.rulesDoc = {}
        self.rulesIgnoreExect = {}
        self.rulesIgnoreContain = {}
        self.rulesGet = {}

    def isJson(self,data: requests) -> bool:
        '''
        判断对象是否能进行json序列化
        :param data:
        :return:
        '''
        try:
            data.json()
        except Exception as e:
            return False
        return True

    def run(self,modelName: Optional[str]=None):
        """
        执行回放
        :param modelName:
        :return:
        """
        scriptPathlist = self.noiseReduction.createTestCase(modelName)
        ALL_RESULT_LIST=[]
        urlTotal = 0
        start_time = datetime.now()
        for scriptPath in scriptPathlist:
            RESULT_LIST =[]
            self.data = self.noiseReduction.getRules(scriptPath)
            self.rulesDoc = self.data.get("rulesDoc", {})
            self.rulesIgnoreExect = self.data.get("rulesIgnoreExect", {})
            self.rulesIgnoreContain = self.data.get("rulesIgnoreContain", {})
            self.rulesGet = self.data.get("rulesGet", {})
            flowDatas = self.data.get("flowDatas", {})
            filter_urls = Global_Map.get('setting').get('filterUrl')
            for i in range(len(flowDatas)):
                respObj = self.callAPI(flowDatas[i])
                urlTotal += 1
                result_dict = {}
                # 默认 result_dict 为 ignore 状态
                result_dict['id'], result_dict['url'], result_dict['method'] = flowDatas[i]['id'], flowDatas[i]['url'], flowDatas[i]['method']
                # 忽略校验的url
                parsed_url = urlparse(flowDatas[i]['url'])
                if filter_urls and any(parsed_url.path.endswith(filteUrl) or flowDatas[i]['url'].startswith(filteUrl) for filteUrl in filter_urls):
                    result_dict['status'] = 'ignore'
                    RESULT_LIST.append(result_dict)
                    continue
                try:
                    if respObj:
                        if respObj.headers.get('Content-Type') and ('application/json' in respObj.headers.get('Content-Type') or self.isJson(respObj)):
                            val = respObj.json()
                            self.diff = assert_json(val, flowDatas[i]['resp'])
                            # 默认对比状态为 pass
                            result_dict['id'], result_dict['url'], result_dict['method'], result_dict['status'] = flowDatas[i]['id'], flowDatas[i]['url'], flowDatas[i]['method'], 'pass'
                            if self.diff:
                                diff_afterRules = self.main(flowDatas[i])
                                if diff_afterRules:
                                    for eachdiff in self.diff:
                                        if "{" in eachdiff["expect"]:
                                            try:
                                                if dict(eval(eachdiff['expect']))[eachdiff['key']] == eachdiff['actual']:
                                                    self.diff.remove(eachdiff)
                                            except:
                                                pass
                                    if self.diff:
                                        result_dict['id'],result_dict['url'],result_dict['method'],result_dict['status'],result_dict['contentList'] = flowDatas[i]['id'],flowDatas[i]['url'],flowDatas[i]['method'],'fail',self.diff
                                        RESULT_LIST.append(result_dict)
                                    else:
                                        RESULT_LIST.append(result_dict)
                                else:
                                    RESULT_LIST.append(result_dict)
                            else:
                                RESULT_LIST.append(result_dict)
                            # 数据替换
                            for rule in self.rulesGet:
                                if rule.get("Path") in flowDatas[i]['url']:
                                    val_deepcopy = copy.deepcopy(val)
                                    id = self.noiseReduction.getValueId(flowDatas, rule)
                                    if id and flowDatas[i]['id'] in id:
                                        for loc in rule['Location'].split('.')[1:]:
                                            try:
                                                loc = int(loc)
                                            except:
                                                pass
                                            try:
                                                val_deepcopy = val_deepcopy[loc]
                                            except:
                                                pass
                                        if val_deepcopy not in [None, []]:
                                            if len(rule['value']) != 0:
                                                # GLOBAL[rule['Location']] = val
                                                flowDatas = eval(str(flowDatas).replace(str(rule['value'][0]), str(val_deepcopy)))
                                                rule['value'].remove(rule['value'][0])
                        else:
                            # 非json数据的对比
                            if respObj.content.decode("utf-8") == flowDatas[i]['resp']:
                                result_dict['status'] = 'pass'
                            else:
                                from difflib import Differ
                                result_dict['status'] = 'fail'
                                expected_lines = flowDatas[i]['resp'].strip().split('\n')
                                actual_lines = respObj.content.decode("utf-8").strip().split('\r\n')
                                d = Differ()
                                diff = list(d.compare(expected_lines, actual_lines))
                                diff_lines = [line for line in diff if line.startswith('- ') or line.startswith('+ ')]
                                result_dict['contentList'] = [{'diff_lines': diff_lines, 'key': 'resp.diff'}]
                            RESULT_LIST.append(result_dict)
                    else:
                        result_dict['status'] = 'fail'
                        RESULT_LIST.append(result_dict)
                except Exception as e:
                    print(f"json解析失败:{e}")
                    return None
            if RESULT_LIST:
                if str(scriptPath).endswith('.json'):
                    key = str(str(scriptPath).split('\\')[0]).split('_流量回放结果')[0]
                else:
                    key = str(str(scriptPath).split('\\')[-1]).split('_流量回放结果')[0]
                ALL_RESULT_LIST.append({'moduleName':key,'info':RESULT_LIST})
        end_time = datetime.now()
        totalTimes = base_utils.time_difference(start_time, end_time)
        moduleNameList = jsonpath.jsonpath(ALL_RESULT_LIST,'$..[?(@.moduleName)]..moduleName')
        moduleCaseTotal =[]
        if ALL_RESULT_LIST:
            for module in jsonpath.jsonpath(ALL_RESULT_LIST,'$..[?(@.moduleName)]'):
                moduleCaseTotal.append(len(module.get('info')))
        replayResult ={'result': ALL_RESULT_LIST,'moduleNameList':moduleNameList,'moduleCaseTotal':moduleCaseTotal,'urlTotal':urlTotal, 'totalTimes':totalTimes}
        ReportUtil().createReport(modelName,replayResult)


    def callAPI(self,flowData):
        '''

        :param flowData:
        :return:
        '''
        req = http_requests.HttpRequests(flowData['url'])
        parsed_url = urlparse(flowData.get('url'))
        # 强制指定header
        if Global_Map.get('setting').get('headers') and isinstance(Global_Map.get('setting').get('headers'),dict):
            flowData['headers'].update(Global_Map.get('setting').get('headers'))
        # 设置登录header
        if Global_Map.get('setting').get('login'):
            for login in Global_Map.get('setting').get('login'):
                header_key = '_'.join([login.get('url').replace(' ', '').replace('-', '_').replace('/', '_'), login.get('header')])
                if isinstance(login, dict) and Global_Map.get(header_key):
                    if login.get('scope'):
                        if [s for s in login.get('scope') if s in parsed_url.path]:
                            flowData['headers'][login.get('header')] = Global_Map.get(header_key)
                    else:
                        flowData['headers'][login.get('header')] = Global_Map.get(header_key)
        # 发送请求
        resp = req.send_request(method=flowData['method'],url=flowData['url'],payload=flowData['body'], header=flowData['headers']).get("response_obj")
        # 循环提取登录信息
        if Global_Map.get('setting').get('login'):
            for login in Global_Map.get('setting').get('login'):
                if isinstance(login,dict) and (parsed_url.path.endswith(login.get('url')) or parsed_url.geturl().endswith(login.get('url'))):
                    token = extract.extract_by_object(resp, login.get('rule'))
                    if isinstance(token,(str,int,bool)):
                        header_key = '_'.join([login.get('url').replace(' ', '').replace('-', '_').replace('/', '_'),login.get('header')])
                        Global_Map.set(header_key, token)
        return resp

    def execRulesIgnoreExect(self,diffeach,flowData):
        '''

        :param diffeach:
        :param flowData:
        :return:
        '''
        for each in self.rulesIgnoreExect:
            if diffeach['key'] == each['Location'] and (each['Path'] == 'ALL' or each['Path'] in flowData["path"]):
                if diffeach in self.diff:
                    self.diff.remove(diffeach)

    def execRulesIgnoreContain(self,diffeach,flowData):
        '''

        :param diffeach:
        :param flowData:
        :return:
        '''
        for each in self.rulesIgnoreContain:
            if str(each['Location']).upper() in str(diffeach['key']).upper() and (each['Path'] == 'ALL' or each['Path'] in flowData["path"]):
                tempkey = [v['key']  for v in self.diff if self.diff ]
                if diffeach['key'] in tempkey :
                    self.diff.remove(diffeach)

    def execRulesGet(self,diffeach,flowData):
        '''

        :param diffeach:
        :param flowData:
        :return:
        '''
        for each in self.rulesGet:
            if ('_').join(str(each['Location']).split('.')[1:]).upper() in str(diffeach['key']).upper() and (flowData["path"] == each['Path'] or each['Path'] == 'ALL'):
                if diffeach in self.diff:
                    self.diff.remove(diffeach)

    def main(self,flowData):
        '''

        :param flowData:
        :return:
        '''
        diff_afterRules = copy.deepcopy(self.diff)
        if diff_afterRules:
            for diffeach in diff_afterRules:
                self.execRulesIgnoreExect(diffeach,flowData)
                self.execRulesIgnoreContain(diffeach,flowData)
                self.execRulesGet(diffeach,flowData)
        return self.diff

if __name__ == '__main__':
    Replay().run()