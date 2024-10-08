#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com

import json
import os
import pathlib
from urllib.parse import urlparse

from harmo import base_utils
from harmo.config import Config
from harmo.extract import extract_by_jmespath
from harmo.global_map import Global_Map
from harmo.operation import json_file
import time

class NoiseReduction:
    def __init__(self):
        self.config = self.getConfig()
        self.rules_IGNORE_CONTAIN, self.rules_IGNORE_EXECT, self.rules_GET = [], [], []
        self.ts =str(int(time.time()))
        self.rules = Global_Map.get()

    def createTestCase(self, modelName: str):
        """
        创建测试用例文件夹
        :param modelName:
        :return:
        """
        scriptPathlist =[]
        if self.config['whetherRecord']:
            playback_folder = 'NoName_流量回放结果_'.replace('NoName', modelName)+self.ts if modelName else 'NoName_流量回放结果_'+self.ts
            Global_Map.set('playback_folder',playback_folder)
            path =  os.path.join(os.getcwd(), playback_folder)
            if not os.path.exists(path):
                os.mkdir(path)
            scriptPathlist.append(path)
        else:
            scriptPathlist = self.config['path']
        return scriptPathlist

    def getFlowData(self, scriptPath):
        if str(scriptPath).endswith('.json'):
            execPath = scriptPath
        else:
            execPath = os.path.join(scriptPath, 'record_results.json')
        if self.config['whetherRecord']:
            flowData = json_file.get_json_data(base_utils.file_absolute_path('record_results.json'))
            with open(execPath, 'w') as ff:
                ff.write(json.dumps(flowData))
        else:
            flowData = json_file.get_json_data(execPath)
        flowDataDeepCopy = [each for each in flowData if each != {} and self.__specialFlowStatus(each)]
        return flowDataDeepCopy

    def getValue(self,data,rules):
        if not isinstance(rules,dict):
            raise ValueError(f"{rules} 规则格式错误(需要是dict类型)，请检查后重新执行！")
        # 通过 Location 提取数据
        value = extract_by_jmespath(data, rules.get('Location'))
        return value

    def getRules(self,scriptPath):
        flowDatas,recond =self.getFlowData(scriptPath),[]
        if self.rules:
            for eachRule in self.rules.get('Rules'):
                if not eachRule.get('Type'):
                    raise ValueError(f"{eachRule} 未定义规则类型，请检查后重新执行！")
                if str(eachRule.get('Type')).upper() not in ['GETVALUE','IGNORE']:
                    raise ValueError(f"出现未支持的规则类型 '{eachRule.get('Type')}' ，请检查后重新执行！")
                if str(eachRule.get('Type')).upper() == 'GETVALUE':
                    if not eachRule.get('Location').startswith('resp.'):
                        raise ValueError(f"{eachRule} GETVALUE 规则的Location字段必须以 resp. 开头，请检查后重新执行！")
                    eachRule['value'],id = [],self.getValueId(flowDatas,eachRule)
                    for data in flowDatas:
                        if id and data.get('id') in id:
                            if self.getValue(data,eachRule):
                                if isinstance(self.getValue(data,eachRule),list):
                                    eachRule['value'].extend(self.getValue(data,eachRule))
                                else:
                                    eachRule['value'].append(self.getValue(data,eachRule))
                        recond.append({'id':data.get('id'),'url':data.get('url'),'method':data.get('method')})
                    self.rules_GET.append(eachRule)
                if str(eachRule.get('Type')).upper() == 'IGNORE':
                    # 和GETVALUE统一Location处理，IGNORE后续的数据是通过“_”来连接的
                    if not eachRule.get('Contain') and not eachRule.get('Location').startswith('resp.'):
                        raise ValueError(f"{eachRule} IGNORE 规则的Contain为False(绝对匹配)时，Location字段必须以 resp. 开头，请检查后重新执行！")
                    if eachRule.get('Location').startswith('resp.'):
                        eachRule['Location'] = eachRule.get('Location').replace('resp.','')
                    eachRule['Location'] = eachRule.get('Location').replace('.','_')
                    if eachRule.get('Contain'):
                        self.rules_IGNORE_CONTAIN.append(eachRule)
                    else:
                        self.rules_IGNORE_EXECT.append(eachRule)
            return {'rules': self.rules.get('Rules'),'status':self.config['whetherRecord'],
                    'ts':self.ts,'flowDatas':flowDatas,'rulesIgnoreContain':self.rules_IGNORE_CONTAIN,
                    'rulesIgnoreExect':self.rules_IGNORE_EXECT,'rulesGet':self.rules_GET}

    def getValueId(self,flowdata,rule):
        id = []
        if 'GETVALUE' in rule.get('Type'):
            for i in range(len(flowdata)):
                if str(rule['Method']).upper()!='MOCK':
                    # rule['Path'] == flowdata[i]['path'] 不能用in，因为path可能重叠
                    if str(rule['Method']).upper() == str(flowdata[i]['method']).upper() and rule['Path'] == flowdata[i]['path']:
                        id.append(flowdata[i]['id'])
                else:
                    if 'MockName' in flowdata[i].keys():
                        if rule['Path'] == flowdata[i]['MockName']:
                            id.append(flowdata[i]['id'])
        else:
            for data in flowdata:
                if rule['Path'] in data['path']:
                    id.append(data['id'])
        return id

    def __specialFlowStatus(self,flowdata):
        status = True
        if 'resp' in flowdata.keys():
            if flowdata.get('resp') == None:
                status=False
        return status

    def getConfig(self):
        result = {}
        configInfo = Global_Map.get()
        result['whetherRecord'], result['path'] = False, []
        if str(configInfo.get('setting').get('status')).upper() == 'NOW':
            result['path'], result['whetherRecord'] = ['record_results.json'], True
        elif str(configInfo.get('setting').get('status')).upper() == 'DEBUG':
            for value in configInfo.get('setting').get('scope'):
                path = os.path.join(Config.project_root_dir, value)
                if not os.path.exists(path):
                    raise ValueError(f"{path} 文件夹没找到，请检查后在执行！")
                else:
                    result['path'] = result['path'] + list(pathlib.Path(path).iterdir())
        else:
            # 获取当前目录下的所有文件和目录
            files_and_directories = os.listdir()
            # 过滤出仅包含目录
            directories = [item for item in files_and_directories if os.path.isdir(item)]
            for eachPath in directories:
                # if self.modelName in eachPath:
                #     path = os.path.join(Config.project_root_dir, eachPath)
                #     result['path'] = result['path'] + list(pathlib.Path(path).iterdir())
                if "_流量回放结果_" in eachPath:
                    path = os.path.join(Config.project_root_dir, eachPath)
                    result['path'] = result['path'] + list(pathlib.Path(path).iterdir())
        if result['path'] == []:
            raise ValueError(f"{result['path']} 文件夹没找到，请检查后在执行！")
        result['baseUrl'] = configInfo.get('setting').get('baseUrl')
        return result
