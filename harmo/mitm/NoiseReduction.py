#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @TIME    : 2024/4/3 15:00
# @Author  : hubiao
# @Email   : 250021520@qq.com

import copy
import json
import os
import pathlib

from harmo import base_utils
from harmo.config import Config
from harmo.global_map import Global_Map
from harmo.operation import json_file, yaml_file
import time
from typing import Optional

class NoiseReduction:
    def __init__(self):
        self.config = self.getConfig()
        self.rules_IGNORE_CONTAIN,self.rules_IGNORE_EXECT,self.rules_GET = [],[],[]
        self.ts =str(int(time.time()))
        self.rules = Global_Map.get()

    def createTestCase(self,modelName:str):
        scriptPathlist =[]
        if self.config['whetherRecord']:
            name = 'NoName_测试脚本文件夹_'.replace('NoName',modelName)+self.ts if modelName else 'NoName_测试脚本文件夹_'+self.ts
            path =  os.path.join(os.getcwd(), name)
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
            execPath = os.path.join(scriptPath,'record_results.json')
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
        location_list = str(rules.get('Location')).split('.')
        value = copy.deepcopy(data)
        for path in location_list:
            try:
                path = int(path)
            except:
                pass
            finally:
                try:
                    value = value[path]
                except:
                    pass
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
                    eachRule['value'],id = [],self.getValueId(flowDatas,eachRule)
                    for data in flowDatas:
                        if id == data.get('id') and id:
                            eachRule['value'].append(self.getValue(data,eachRule))
                        recond.append({'id':data.get('id'),'url':data.get('url'),'method':data.get('method')})
                    self.rules_GET.append(eachRule)
                if str(eachRule.get('Type')).upper() == 'IGNORE':
                    if eachRule.get('Contain'):
                        self.rules_IGNORE_CONTAIN.append(eachRule)
                    else:
                        self.rules_IGNORE_EXECT.append(eachRule)
            return {'rules': self.rules['Rules'],'status':self.config['whetherRecord'],
                    'NotifyUser': self.config['NotifyUser'],
                    'ts':self.ts,'flowDatas':flowDatas,'rulesIgnoreContain':self.rules_IGNORE_CONTAIN,
                    'rulesIgnoreExect':self.rules_IGNORE_EXECT,'rulesGet':self.rules_GET}

    def getValueId(self,flowdata,rule):
        id =None
        if 'AfterAPI' in rule.keys():
            for i in range(len(flowdata)):
                if str(rule['AfterAPI']['Method']).upper()!='MOCK':
                    if str(rule['AfterAPI']['Method']).upper() == str(flowdata[i]['method']).upper() and rule['AfterAPI']['Path'] == flowdata[i]['path']:
                        id=flowdata[i]['id']
                else:
                    if 'MockName' in flowdata[i].keys():
                        if rule['AfterAPI']['Path'] == flowdata[i]['MockName']:
                            id = flowdata[i]['id']
        else:
            for data in flowdata:
                if rule['Path'] in data['path']:
                    id = data['id']
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
        if str(configInfo.get('Setting').get('Status')).upper() == 'NOW':
            result['path'], result['whetherRecord'] = ['record_results.json'], True
        elif str(configInfo.get('Setting').get('Status')).upper() == 'DEBUG':
            for value in configInfo.get('Setting').get('Scope'):
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
                if "_测试脚本文件夹_" in eachPath:
                    path = os.path.join(Config.project_root_dir, eachPath)
                    result['path'] = result['path'] + list(pathlib.Path(path).iterdir())
        if result['path'] == []:
            raise ValueError(f"{result['path']} 文件夹没找到，请检查后在执行！")
        result['Url'], result['User'], result['PSW'], result['NotifyUser'] = configInfo.get('Setting').get('Url'), \
            configInfo.get('Setting').get('User'), \
            configInfo.get('Setting').get('PSW'), \
            configInfo.get('Setting').get('NotifyUser')
        return result
