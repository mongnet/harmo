import requests, json, yaml, copy, time, os
from luban_common import base_utils
from report import *
from NoiseReduction import *
from ExecRules import *
from ExecScript import *
from _global import *


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
    print(errorList)
    return errorList
def callWeChatAPI(switch, info, tips, userList):
    if str(switch).upper() == 'TEST':
        # 测试
        url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=8052542e-1f3f-4d98-a9a0-559223599e98'
    else:
        # 正式
        url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d33955e6-7c6a-4ac0-a7e7-06ce37a408e8'
    header = {'Content-Type': 'application/json'}
    body = {
        "msgtype": "markdown",
        "markdown": {
            "content": info,
        }
    }
    if info != "ALL PASS!!!":
        res = requests.post(url, json=body, headers=header)
    body_info = {
        "msgtype": "text",
        "text": {
            "content": tips,
            "mentioned_mobile_list": userList
        }
    }
    res = requests.post(url, json=body_info, headers=header)
    return res.json()
def execScript(modelName,testDocName):
    scriptPathlist = NoiseReduction().createTestCase(modelName,testDocName)
    FLOW_LIST,ALL_ERROR_LIST=[],[]
    for scriptPath in scriptPathlist:
        ERROR_LIST =[]
        flowData = ExecScript(scriptPath).updateToken(NoiseReduction().createScript(scriptPath))
        for i in range(len(flowData)):
            FLOW_LIST.append({'id':base_utils.generate_random_str(16),'url':flowData[i]['url'],'method':flowData[i]['method']})
            result = ExecScript( scriptPath).callAPI(flowData[i])
            for rule in ExecRules(scriptPath).rulesGet:
                try:
                    if result!=None:
                        if result.status_code in [200, 500]:
                            if 'PNG' not in result.text:
                                val = result.json()
                except:
                    print("脚本报错！result json 失败")
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
                        GLOBAL[rule['Location']] = val
                        flowData = eval(str(flowData).replace(str(rule['value'][0]), val))
                        rule['value'].remove(rule['value'][0])
            if result!=None :
                if result.status_code in [200,500]:
                    if 'PNG' not in result.text:
                        diff = assert_json(result.json(), flowData[i]['resp'])
                        if diff!=[]:
                            error_dict={}
                            diff_afterRules = ExecRules(scriptPath,diff).main(flowData[i])
                            if diff_afterRules!=[]:
                                for eachdiff in diff:
                                    if "{" in eachdiff["expect"]:
                                        try:
                                            if dict(eval(eachdiff['expect']))[eachdiff['key']] == eachdiff['actual']:
                                                diff.remove(eachdiff)
                                        except:
                                            pass
                                error_dict['id'],error_dict['url'],error_dict['method'],error_dict['contentList'] = flowData[i]['id'],flowData[i]['url'],flowData[i]['method'],diff
                                ERROR_LIST.append(error_dict)
        key = str(str(scriptPath).split('\\')[-1]).split('_')[0]
        module = str(str(scriptPath).split('\\')[-2]).split('_')[0]
        ALL_ERROR_LIST.append({'name':key,'info':ERROR_LIST,'moduleName':module})
    print(FLOW_LIST)
    moduleNameList = list(set([each['moduleName'] for each in ALL_ERROR_LIST]))
    moduleCaseTotal =[]
    for name in moduleNameList:
        num = 0
        for case in ALL_ERROR_LIST:
            if case['moduleName'] == name:
                num=num+1
        moduleCaseTotal.append(num)

    data ={'error': ALL_ERROR_LIST,'moduleNameList':moduleNameList,'moduleCaseTotal':moduleCaseTotal}
    #ReportUtil().createReport(data)
    print(data)







if __name__ == '__main__':
    execScript('Center模块','职务管理-编辑职务')
    # noise_reduction()
