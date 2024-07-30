#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com

import os
from datetime import datetime

import jsonpath

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
    actual = dict(eval(str(actual).replace('true', 'True').replace('false', 'False')))
    for key in actual.keys():
        temp_dict = {}
        if '{' not in str(actual[key]):
            if len(actual[key]) != 0:
                for i in range(len(actual[key])):
                    if actual[key][i] == 'null': actual[key][i] = 'None'
                    if 'false' in str(actual[key][i]): actual[key][i] = str(actual[key][i]).replace('false', 'False')
                    if 'true' in str(actual[key][i]): actual[key][i] = str(actual[key][i]).replace('true', 'True')
                if isinstance(actual[key][0], (str, float, int)):
                    try:
                        if len(actual[key]) == len(expect[key]):
                            if list(set(actual[key]).difference(set(expect[key]))) != []:
                                temp_dict['key'] = key
                                temp_dict['expect'] = expect[key]
                                temp_dict['actual'] = actual[key]
                        else:
                            temp_dict['key'] = key
                            temp_dict['expect'] = expect[key]
                            temp_dict['actual'] = actual[key]
                    except:
                        temp_dict['key'] = key
                        temp_dict['expect'] = str(expect)
                        temp_dict['actual'] = actual[key]
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

    def run(self,modelName):
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
                result_dict['id'], result_dict['url'], result_dict['method'], result_dict['status'] = flowDatas[i]['id'], flowDatas[i]['url'], flowDatas[i]['method'], 'ignore'
                # 忽略校验的url
                parsed_url = urlparse(flowDatas[i]['url'])
                if filter_urls and any(parsed_url.path.endswith(filteUrl) or flowDatas[i]['url'].startswith(filteUrl) for filteUrl in filter_urls):
                    RESULT_LIST.append(result_dict)
                    continue
                try:
                    if respObj:
                        if respObj.headers.get('Content-Type') and 'application/json' in respObj.headers.get('Content-Type'):
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
                                whetherCheck = False
                                id = self.noiseReduction.getValueId(flowDatas, rule)
                                if id == flowDatas[i]['id']:
                                    whetherCheck = True
                                    for loc in rule['Location'].split('.')[1:]:
                                        try:
                                            loc = int(loc)
                                        except:
                                            pass
                                        try:
                                            val = val[loc]
                                        except:
                                            pass
                                if val not in [None, []] and whetherCheck:
                                    if len(rule['value']) != 0:
                                        # GLOBAL[rule['Location']] = val
                                        flowDatas = eval(str(flowDatas).replace(str(rule['value'][0]), str(val)))
                                        rule['value'].remove(rule['value'][0])
                        else:
                            RESULT_LIST.append(result_dict)
                    else:
                        RESULT_LIST.append(result_dict)
                except Exception as e:
                    print(f"json解析失败:{e}")
                    return None
            if RESULT_LIST:
                if str(scriptPath).endswith('.json'):
                    key = str(str(scriptPath).split('\\')[0]).split('_测试脚本')[0]
                else:
                    key = str(str(scriptPath).split('\\')[-1]).split('_测试脚本')[0]
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
        if Global_Map.get("setting").get("headers") and isinstance(Global_Map.get("setting").get("headers"),dict):
            flowData['headers'].update(Global_Map.get("setting").get("headers"))
        if Global_Map.get(Global_Map.get('setting').get('login').get("header")):
            flowData['headers'][Global_Map.get('setting').get('login').get("header")] = Global_Map.get(Global_Map.get('setting').get('login').get("header"))
        resp = req.send_request(method=flowData['method'],url=flowData['url'],payload=flowData['body'], header=flowData['headers']).get("response_obj")
        parsed_url = urlparse(flowData.get('url'))
        if parsed_url.path.endswith(Global_Map.get('setting').get('login').get("url")):
            token = extract.extract_by_object(resp, Global_Map.get('setting').get('login').get("rule"))
            Global_Map.set(Global_Map.get('setting').get('login').get("header"),token)
        return resp

    def execRulesIgnoreExect(self,data,flowData):
        '''

        :param data:
        :param flowData:
        :return:
        '''
        for each in self.rulesIgnoreExect:
            if data['key'] == each['Location'] and (flowData["path"] == each['Path'] or each['Path'] == 'ALL'):
                self.diff.remove(data)

    def execRulesIgnoreContain(self,data,flowData):
        '''

        :param data:
        :param flowData:
        :return:
        '''
        for each in self.rulesIgnoreContain:
            if str(each['Location']).upper() in str(data['key']).upper() and (flowData["path"] == each['Path'] or each['Path'] == 'ALL'):
                tempkey = [v['key']  for v in self.diff if self.diff ]
                if data['key'] in tempkey : self.diff.remove(data)

    def execRulesGet(self,data,flowData):
        '''

        :param data:
        :param flowData:
        :return:
        '''
        for each in self.rulesGet:
            if ('_').join(str(each['Location']).split('.')[1:]).upper() in str(data['key']).upper() and (
                    flowData["path"] == each['Path'] or each['Path'] == 'ALL'):
                self.diff.remove(data)

    def main(self,flowData):
        '''

        :param flowData:
        :return:
        '''
        if self.diff:
            for diffeach in self.diff:
                self.execRulesIgnoreExect(diffeach,flowData)
                self.execRulesIgnoreContain(diffeach,flowData)
                self.execRulesGet(diffeach,flowData)
        return self.diff

if __name__ == '__main__':
    Replay().run('职务管理-编辑职务')