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
        self.rules_IGNORE_CONTAIN,self.rules_IGNORE_EXECT,self.rules_GET,self.rules_DOC = [],[],[],[]
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
        location_list = str(dict(rules)['Location']).split('.')
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
        flowData,recond =self.getFlowData(scriptPath),[]
        if self.rules:
            for eachRule in self.rules.get('Rules'):
                if str(eachRule['Type']).upper() == 'GETVALUE':
                    eachRule['value'],id =[],self.getValueId(flowData,eachRule)
                    for data in flowData:
                        if id == data['id'] and id!=None:
                            eachRule['value'].append(self.getValue(data,eachRule))
                        recond.append({'id':data['id'],'url':data['url'],'method':data['method']})
                    self.rules_GET.append(eachRule)
                if str(eachRule['Type']).upper() == 'IGNORE':
                    if eachRule['Contain']:
                        self.rules_IGNORE_CONTAIN.append(eachRule)
                    else:
                        self.rules_IGNORE_EXECT.append(eachRule)
                if str(eachRule['Type']).upper() == 'DOC':
                    self.rules_DOC.append(eachRule)
            return {'rules': self.rules['Rules'],'status':self.config['whetherRecord'],
                    'model': self.config['Model'], 'NotifyUser': self.config['NotifyUser'],
                    'ts':self.ts,'flowData':flowData,'rulesIgnoreContain':self.rules_IGNORE_CONTAIN,
                    'rulesIgnoreExect':self.rules_IGNORE_EXECT,'rulesGet':self.rules_GET,
                    'rulesDoc':self.rules_DOC}

    def getValueId(self,flowdata,rule):
        id =None
        if 'AfterAPI' in rule.keys() :
            for i in range(len(flowdata)):
                if str(rule['AfterAPI']['Method']).upper()!='MOCK':
                    if str(rule['AfterAPI']['Method']).upper()==str(flowdata[i]['method']).upper() and rule['AfterAPI']['Path'] in flowdata[i]['path']:
                        id=flowdata[i+1]['id']
                else:
                    if 'MockName' in flowdata[i].keys():
                        if rule['AfterAPI']['Path'] == flowdata[i]['MockName']:
                            id = flowdata[i+1]['id']
        else:
            for data in flowdata:
                if rule['Path'] in data['path']:
                    id = data['id']
        return id

    def __specialFlowStatus(self,flowdata):
        status = True
        if 'resp' in flowdata.keys():
            if flowdata['resp'] ==None:
                status=False
        return status

    def getConfig(self):
        result = {}
        configInfo = Global_Map.get()
        result['whetherRecord'], result['path'] = False, []
        if str(configInfo['Setting']['Status']).upper() == 'NOW':
            result['path'], result['whetherRecord'] = ['record_results.json'], True
        elif str(configInfo['Setting']['Status']).upper() == 'DEBUG':
            for value in configInfo['Setting']['Scope']:
                path = os.path.join(Config.project_root_dir, value)
                if not os.path.exists(path):
                    raise ValueError(f"{path} 文件夹没找到，请检查后在执行！")
                else:
                    result['path'] = result['path'] + list(pathlib.Path(path).iterdir())
        else:
            for eachPath in os.listdir():
                if "_测试脚本集" in eachPath:
                    path = os.getcwd() + os.sep + eachPath
                    pathAbs = path + os.sep
                    path_list = pathlib.Path(pathAbs)
                    result['path'] = result['path']+list(path_list.iterdir())
        if result['path'] == []:
            raise ValueError(f"{result['path']} 文件夹没找到，请检查后在执行！")
        result['Model'] = configInfo.get('Setting').get('Model')
        result['Url'], result['User'], result['PSW'], result['NotifyUser'] = configInfo.get('Setting').get('Url'), \
            configInfo.get('Setting').get('User'), \
            configInfo.get('Setting').get('PSW'), \
            configInfo.get('Setting').get('NotifyUser')
        return result


