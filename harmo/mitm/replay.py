#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com

import jsonpath
from harmo import base_utils
from harmo.mitm.report import ReportUtil
from harmo.msg.robot import WeiXin
from harmo.operation import yaml_file
from ExecRules import *
from ExecScript import *

def assert_json(actual, expect):
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
    if errorList:
        print(errorList)
    return errorList

def execScript(modelName,testDocName=None):
    Global_Map.sets(yaml_file.get_yaml_data(base_utils.file_absolute_path("conifg/config.yaml")))
    scriptPathlist = NoiseReduction().createTestCase(modelName,testDocName)
    FLOW_LIST,ALL_RESULT_LIST=[],[]
    urlTotal = 0
    for scriptPath in scriptPathlist:
        RESULT_LIST =[]
        flowData = ExecScript(scriptPath).updateToken(NoiseReduction().createScript(scriptPath))
        for i in range(len(flowData)):
            FLOW_LIST.append({'id':base_utils.generate_random_str(16),'url':flowData[i]['url'],'method':flowData[i]['method']})
            result = ExecScript(scriptPath).callAPI(flowData[i])
            urlTotal += 1
            result_dict = {}
            # 过滤url
            from urllib.parse import urlparse
            filter_urls = Global_Map.get('Setting').get('filterUrl')
            parsed_url = urlparse(flowData[i]['url'])
            if filter_urls and any(parsed_url.path.endswith(filteUrl) or flowData[i]['url'].startswith(filteUrl) for filteUrl in filter_urls):
                result_dict['id'], result_dict['url'], result_dict['method'], result_dict['status'] = \
                    flowData[i]['id'], flowData[i]['url'], flowData[i]['method'], 'ignore'
                RESULT_LIST.append(result_dict)
                continue
            for rule in ExecRules(scriptPath).rulesGet:
                try:
                    if result:
                        if result.status_code in [200, 500]:
                            if 'PNG' not in result.text:
                                val = result.json()
                except Exception as e:
                    print(f"脚本报错！result json 失败:{e}")
                    return None
                whetherCheck = False
                id = NoiseReduction().getValueId(flowData,rule)
                if id == flowData[i]['id']:
                    whetherCheck = True
                    for loc in rule['Location'].split('.')[1:]:
                        try: loc = int(loc)
                        except:pass
                        try:
                            val = val[loc]
                        except:
                            pass
                if val not in [None, []] and whetherCheck == True:
                    if len(rule['value']) != 0:
                        # GLOBAL[rule['Location']] = val
                        flowData = eval(str(flowData).replace(str(rule['value'][0]), val))
                        rule['value'].remove(rule['value'][0])
            if result:
                if result.status_code in [200,500]:
                    if 'PNG' not in result.text:
                        diff = assert_json(result.json(), flowData[i]['resp'])
                        if diff:
                            diff_afterRules = ExecRules(scriptPath,diff).main(flowData[i])
                            if diff_afterRules:
                                for eachdiff in diff:
                                    if "{" in eachdiff["expect"]:
                                        try:
                                            if dict(eval(eachdiff['expect']))[eachdiff['key']] == eachdiff['actual']:
                                                diff.remove(eachdiff)
                                        except:
                                            pass
                                if diff:
                                    result_dict['id'],result_dict['url'],result_dict['method'],result_dict['status'],result_dict['contentList'] = flowData[i]['id'],flowData[i]['url'],flowData[i]['method'],'fail',diff
                                    RESULT_LIST.append(result_dict)
                                else:
                                    result_dict['id'], result_dict['url'], result_dict['method'], result_dict['status'] = flowData[i]['id'], flowData[i]['url'], flowData[i]['method'], 'pass'
                                    RESULT_LIST.append(result_dict)
                            else:
                                result_dict['id'], result_dict['url'], result_dict['method'], result_dict['status'] = \
                                flowData[i]['id'], flowData[i]['url'], flowData[i]['method'], 'pass'
                                RESULT_LIST.append(result_dict)
                        else:
                            result_dict['id'], result_dict['url'], result_dict['method'], result_dict['status'] = \
                            flowData[i]['id'], flowData[i]['url'], flowData[i]['method'], 'pass'
                            RESULT_LIST.append(result_dict)
        if RESULT_LIST:
            key = str(str(scriptPath).split('\\')[-1]).split('_')[0]
            module = str(str(scriptPath).split('\\')[-2]).split('_')[0]
            ALL_RESULT_LIST.append({'name':key,'info':RESULT_LIST,'moduleName':module})
    moduleNameList = jsonpath.jsonpath(ALL_RESULT_LIST,'$..[?(@.moduleName)]..moduleName')
    moduleCaseTotal =[]
    if ALL_RESULT_LIST:
        for module in jsonpath.jsonpath(ALL_RESULT_LIST,'$..[?(@.moduleName)]'):
            moduleCaseTotal.append(len(module.get('info')))
    data ={'result': ALL_RESULT_LIST,'moduleNameList':moduleNameList,'moduleCaseTotal':moduleCaseTotal,'urlTotal':urlTotal}
    weixin_robot = Global_Map.get('Setting').get('weixin_robot')
    result = ReportUtil().createReport(data)
    if weixin_robot:
        WeiXin().send_file(hookkey=weixin_robot, file=result)

if __name__ == '__main__':
    execScript('Center模块','职务管理-编辑职务')