import requests, json, yaml, copy, time, os
from harmo import base_utils
from harmo.global_map import Global_Map
from harmo.msg.robot import WeiXin

def setToken():
    data = getConfig()
    body = {"password": data['PSW'], "username": data['User']}
    headers = {"Content-Type": "application/json"}
    res = requests.post(data['Url'], json=body, headers=headers)
    return res.json()['data']['token']


def getConfig():
    result = {}
    with open('config.yaml', 'r', encoding='utf-8') as file:
        # configInfo = yaml.load(file.read())
        configInfo = yaml.load(file,Loader=yaml.FullLoader)
        file.close()
    if str(configInfo['Setting']['Status']).upper() == 'NOW':
        result['path'] = 'script.json'
        result['whetherRecord'] = 1
    else:
        result['path'] = []
        result['whetherRecord'] = 0
        if str(configInfo['Setting']['Status']).upper() == 'DEBUG':
            for value in configInfo['Setting']['Scope']:
                path = os.getcwd() + os.sep + value
                if not os.path.exists(path):
                    print("测试脚本文件夹没找到，请检查后在执行！")
                else:
                    pathAbs = path + os.sep
                    result['path'].append(pathAbs)
        else:
            for eachPath in os.listdir():
                if "测试脚本文件夹" in eachPath:
                    path = os.getcwd() + os.sep + eachPath
                    pathAbs = path + os.sep
                    result['path'].append(pathAbs)
        if result['path'] == []: print("测试脚本文件夹没找到，请检查后在执行！")
    result['Model'] = configInfo['Setting']['Model']
    result['Url'], result['User'], result['PSW'], result['NotifyUser'] = configInfo['Setting']['Url'], \
                                                                         configInfo['Setting']['User'], \
                                                                         configInfo['Setting']['PSW'], \
                                                                         configInfo['Setting']['NotifyUser']
    return result


def noise_reduction(testDocName):
    try:
        ts, path, rulesList = str(int(time.time())), '', []
        config = getConfig()
        scriptPathlist, flowDataList = [], []
        if config['whetherRecord'] == 1:
            if testDocName != None:
                name = testDocName + '_测试脚本文件夹_' + ts
            else:
                name = 'NoName_测试脚本文件夹_' + ts
            os.mkdir(name)
            path = os.getcwd() + os.sep + name + os.sep
            scriptPathlist.append(path)
        else:
            scriptPathlist = config['path']
        for scriptPath in scriptPathlist:
            execPath = scriptPath + os.sep + 'script.json'
            if config['whetherRecord'] == 1:
                with open('script.json', 'r', encoding='utf-8') as fscript:
                    flowData = json.loads(fscript.read())
                with open(execPath, 'w') as ff:
                    ff.write(json.dumps(flowData))
            else:
                with open(execPath, 'r') as f1:
                    flowData = json.loads(f1.read())
            with open('rules.yaml', 'r', encoding='utf-8') as r:
                # rules = yaml.load(r.read())
                rules = yaml.load(r,Loader=yaml.FullLoader)
            for rulesValueEach in rules['Rules']:
                rulesValueEach['Value'] = []
                for data in flowData:
                    if data == {}:
                        flowData.remove(data)
                    else:
                        if '{' in rulesValueEach['Path']:
                            if (rulesValueEach['Path'].split('{')[0] in data['path']) and (
                                    rulesValueEach['Method'] == data['method']):
                                location_list = str(rulesValueEach['Location']).split('.')
                                val = copy.deepcopy(data)
                                if str(rulesValueEach['Type']).upper() == 'GETVALUE':
                                    for path in location_list:
                                        if path.isdigit(): path = int(path)
                                        try:
                                            val = val[path]
                                        except:
                                            pass
                                    rulesValueEach['Value'].append(val)
                        else:
                            if (rulesValueEach['Path'] == data['path']) and (
                                    rulesValueEach['Method'] == data['method']):
                                location_list = str(rulesValueEach['Location']).split('.')
                                val = copy.deepcopy(data)
                                if str(rulesValueEach['Type']).upper() == 'GETVALUE':
                                    for path in location_list:
                                        if path.isdigit(): path = int(path)
                                        try:
                                            val = val[path]
                                        except:
                                            pass
                                    rulesValueEach['Value'].append(val)
            rulesList.append(rules['Rules'])
            filePath, recond = scriptPath + os.sep + ts + '_回放列表.txt', ''
            for value in flowData:
                if value != {}: recond = recond + value['id'] + ', ' + value['url'] + ', method: ' + value[
                    'method'] + '\r\n'
            with open(filePath, 'w') as f:
                f.write(recond)
            flowDataList.append(flowData)
        return {'flowData': flowDataList, 'rules': rulesList, 'ts': ts, 'status': config['whetherRecord'],
                'path': scriptPathlist, 'model': config['Model'], 'NotifyUser': config['NotifyUser']}
    except:
        print("降噪错误，查看数据是否被清理干净")


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

def execScript(testDocName):
    access_token = setToken()
    data = noise_reduction(testDocName)
    flowDataList, rulesList = data['flowData'], data['rules']
    rules_GET, rules_IGNORE_CONTAIN, rules_IGNORE_EXECT = [], [], []
    num, ERROR_ALL_INFO, weChat = 0, [], ''
    ERROR_ALL_INFO_location = 'AllInfo_' + data['ts'] + '.txt'
    for flowData in flowDataList:
        ERROR_LIST = []
        rules = rulesList[int(flowDataList.index(flowData))]
        for rule in rules:
            if str(rule['Type']).upper() == "IGNORE":
                if rule['Contain']:
                    rules_IGNORE_CONTAIN.append({'Path': rule['Path'], 'key': rule['Location']})
                else:
                    rules_IGNORE_EXECT.append({'Path': rule['Path'], 'key': rule['Location']})
        for value in rules:
            if str(value['Type']).upper() == 'GETVALUE':
                rules_GET.append(value)
        for i in range(len(flowData)):
            if flowData[i] != {}:
                flowData[i]['headers']['access-token'] = access_token
                if 'GET' == str(flowData[i]['method']).upper():
                    result = requests.get(flowData[i]['url'], headers=flowData[i]['headers'])
                    print(flowData[i]['url'])
                    print(flowData[i]['body'])
                    print(result.text)
                if 'POST' == str(flowData[i]['method']).upper():
                    if 'Content-Type' in dict(flowData[i]['headers']).keys():
                        if 'multipart/form-data' in dict(flowData[i]['headers'])['Content-Type']:
                            try:
                                ruleListPath = [eachPath['Path'] for eachPath in rules]
                                docName = "b1.png"
                                try:
                                    pathTempList = [value for value in flowData[i]['path'].split('/')]
                                    if pathTempList[-1].isdigit():
                                        pathTemp = "/".join(pathTempList[:-1]) + '/{id}'
                                    else:
                                        pathTemp = flowData[i]['path']
                                except:
                                    pathTemp = flowData[i]['path']
                                if pathTemp in ruleListPath:
                                    if 'DOC' in dict(rules[int(ruleListPath.index(pathTemp))]).keys():
                                        path = os.path.dirname(os.path.abspath(__file__)) + os.sep + \
                                               rules[int(ruleListPath.index(pathTemp))]['DOC']
                                        docName = rules[int(ruleListPath.index(pathTemp))]['DOC']
                                    else:
                                        path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "b1.png"
                                else:
                                    path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "b1.png"
                            except:
                                path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "b1.png"
                            if flowData[i]['body']['doc'] == 'file':
                                fileinfo = {"file": (docName, open(path, "rb"), "image/png")}
                            else:
                                fileinfo = {"attachment": (docName, open(path, "rb"), "image/png")}
                            del flowData[i]['body']['doc']
                            del flowData[i]['headers']['Content-Type']
                            result = requests.post(flowData[i]['url'], data=flowData[i]['body'],
                                                   headers=flowData[i]['headers'], files=fileinfo)
                        else:
                            result = requests.post(flowData[i]['url'], json=flowData[i]['body'],
                                                   headers=flowData[i]['headers'])
                    else:
                        result = requests.post(flowData[i]['url'], json=flowData[i]['body'],
                                               headers=flowData[i]['headers'])
                    print(flowData[i]['url'])
                    print(flowData[i]['body'])
                if 'DELETE' == str(flowData[i]['method']).upper():
                    result = requests.delete(flowData[i]['url'], headers=flowData[i]['headers'])
                    print(result.text)
                for rule in rules_GET:
                    try:
                        val = result.json()
                    except:
                        weixin_robot = Global_Map.get("Setting").get("weixin_robot")
                        if weixin_robot:
                            md = f'''
                                    # 脚本挂了，快去查原因！
                                    >脚本名：<font color="comment">{str(str(data['path'][num]).split('zhgd_recordjob')[-1]).split('_')[0][1:]}</font>'''
                            WeiXin().send_message_markdown(hookkey=weixin_robot, content=md)
                        return None
                    whetherCheck = False
                    if "{" in rule['Path']:
                        if rule['Path'].split('{')[0] in flowData[i]['path'] and rule['Method'] == flowData[i][
                            'method']:
                            whetherCheck = True
                            for loc in rule['Location'].split('.')[1:]:
                                if loc.isdigit(): loc = int(loc)
                                try:
                                    val = val[loc]
                                except:
                                    pass
                    else:
                        if rule['Path'] == flowData[i]['path'] and rule['Method'] == flowData[i]['method']:
                            whetherCheck = True
                            for loc in rule['Location'].split('.')[1:]:
                                if loc.isdigit(): loc = int(loc)
                                try:
                                    val = val[loc]
                                except:
                                    pass
                    if val not in [None, []] and whetherCheck == True:
                        index, id = 0, ''
                        if 'index' in rule.keys():
                            flowDatatempList = []
                            for flowDataeach in flowData:
                                if flowDataeach['url'] == flowData[i]['url']:
                                    flowDatatempList.append(flowDataeach)
                            id = flowDatatempList[int(rule['index'])]['id']
                            index = int(rule['index'])
                        try:
                            if len(rule['Value']) != 0 and rule['Value'][index] not in ["", [], None]:
                                if 'index' not in rule.keys() or flowData[i]['id'] == id:
                                    flowData = eval(str(flowData).replace(str(rule['Value'][index]), val))
                                    rule['Value'].remove(rule['Value'][index])
                        except:
                            pass
                diff = assert_json(result.json(), flowData[i]['resp'])
                if diff != []:
                    error_dict = {}
                    for diffEach in diff[:]:
                        for eachContainKey in rules_IGNORE_EXECT:
                            if diffEach['key'] == eachContainKey['key'] and (
                                    flowData[i]["path"] == eachContainKey['Path'] or eachContainKey['Path'] == 'ALL'):
                                try:
                                    diff.remove(diffEach)
                                except:
                                    pass
                        for eachKey in rules_IGNORE_CONTAIN:
                            if str(eachKey['key']).upper() in str(diffEach['key']).upper() and (
                                    flowData[i]["path"] == eachKey['Path'] or eachKey['Path'] == 'ALL'):
                                tempkey = []
                                if diff != []:
                                    for v in diff:
                                        tempkey.append(v['key'])
                                if diffEach['key'] in tempkey:
                                    try:
                                        diff.remove(diffEach)
                                    except:
                                        pass
                        for eachKey in rules_GET:
                            if ('_').join(str(eachKey['Location']).split('.')[1:]).upper() in str(
                                    diffEach['key']).upper() and (
                                    flowData[i]["path"] == eachKey['Path'] or eachKey['Path'] == 'ALL'):
                                try:
                                    diff.remove(diffEach)
                                except:
                                    pass

                    if diff != []:
                        for eachdiff in diff:
                            if "{" in eachdiff["expect"]:
                                try:
                                    if dict(eval(eachdiff['expect']))[eachdiff['key']] == eachdiff['actual']:
                                        diff.remove(eachdiff)
                                except:
                                    pass
                        error_dict['id'] = flowData[i]['id']
                        error_dict['url'] = flowData[i]['url']
                        error_dict['method'] = flowData[i]['method']
                        error_dict['contentList'] = diff
                        ERROR_LIST.append(error_dict)
        print(ERROR_LIST)
        fileName = data['path'][num] + os.sep + data['ts'] + '_比对结果.txt'
        errorinfo = ''
        if ERROR_LIST != []:
            for value in ERROR_LIST:
                errorinfo = errorinfo + str(value) + '\r\n'
                ERROR_ALL_INFO.append(
                    {"Name": str(str(data['path'][num]).split('zhgd_recordjob')[-1]).split('_')[0][1:],
                     'Status': "Failed", "location": fileName})
        else:
            errorinfo = 'Test PASS!'
            ERROR_ALL_INFO.append(
                {"Name": str(str(data['path'][num]).split('zhgd_recordjob')[-1]).split('_')[0][1:], 'Status': "Pass",
                 "location": fileName})

        with open(fileName, 'w', encoding='utf-8') as ferror:
            ferror.write(errorinfo)
        num = num + 1
    ERROR_ALL_INFO_NoDuplicate = []
    for value in ERROR_ALL_INFO:
        if value not in ERROR_ALL_INFO_NoDuplicate:
            ERROR_ALL_INFO_NoDuplicate.append(value)
    info = '\r\n'.join([str(value) for value in ERROR_ALL_INFO_NoDuplicate])
    for infoValue in ERROR_ALL_INFO_NoDuplicate:
        del infoValue['location']
        if 'Pass' in str(infoValue):
            markdown = str(infoValue).replace('Pass', '<font color="info">Pass</font>')
        else:
            markdown = str(infoValue).replace('Failed', '<font color="warning">Failed</font>')
        if 'Failed' in markdown:
            weChat = weChat + str(markdown) + '\r\n'
    if "Failed" not in weChat:
        weChat = "ALL PASS!!!"
        md = f'''
                # {weChat}
                >Smoking Testing PASS!!! 测试人员麻溜的过来搬砖！本次一共执行了 {str(len(ERROR_ALL_INFO_NoDuplicate))} 条用例~'''
    else:
        md = f'''
                # {weChat}
                >Smoking Testing Failed!!! 测试人员跑失败了，去瞅瞅！本次一共执行了 {str(len(ERROR_ALL_INFO_NoDuplicate))} 条用例~'''
    weixin_robot = Global_Map.get("Setting").get("weixin_robot")
    if weixin_robot:
        WeiXin().send_message_markdown(hookkey=weixin_robot, content=md)
    with open(ERROR_ALL_INFO_location, 'w') as finfo:
        finfo.write(info)
    return ERROR_LIST


if __name__ == '__main__':
    execScript('Training_KnowledgeReporisty')
    # noise_reduction()
